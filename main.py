#!/usr/bin/env python3
"""
Plot 3 points (trajectories) in 3D from a wide-format CSV over a 5-minute window.

Expected CSV columns (semicolon- or comma-delimited):
Time (or SimTime), N0x, N0y, N0z, N1x, N1y, N1z, N2x, N2y, N2z

Usage examples:
  python plot_3points_3d_wide.py --csv file_number1.csv --mp4 out.mp4 --fps 12
  python plot_3points_3d_wide.py --csv file_number1.csv --gif out.gif --fps 8
"""

import argparse, sys
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa
from matplotlib import animation

def _normalize_cols(cols):
    return [c.strip().lower().replace(" ", "") for c in cols]

def load_data_wide(csv_path: str) -> pd.DataFrame:
    raw = pd.read_csv(csv_path, sep=None, engine="python")  # auto-detect delimiter
    if raw.empty:
        raise ValueError("CSV is empty")

    norm_cols = _normalize_cols(raw.columns)
    col_map = {norm_cols[i]: raw.columns[i] for i in range(len(raw.columns))}

    # Handle alias for time column
    if "time" not in col_map and "simtime" in col_map:
        col_map["time"] = col_map["simtime"]

    req = ["time",
           "n0x","n0y","n0z",
           "n1x","n1y","n1z",
           "n2x","n2y","n2z"]
    missing = [c for c in req if c not in col_map]
    if missing:
        raise ValueError(f"Missing required columns: {missing}. Found: {list(raw.columns)}")

    time_col = col_map["time"]
    df = raw.copy()
    df["time"] = pd.to_datetime(df[time_col], errors="coerce", utc=True)
    if df["time"].isna().any():
        # fallback: epoch seconds
        df["time"] = pd.to_datetime(raw[time_col].astype(float), unit="s", utc=True)

    long_rows = []
    for _, row in df.iterrows():
        t = row["time"]
        for pid in [0,1,2]:
            x = pd.to_numeric(row[col_map[f"n{pid}x"]], errors="coerce")
            y = pd.to_numeric(row[col_map[f"n{pid}y"]], errors="coerce")
            z = pd.to_numeric(row[col_map[f"n{pid}z"]], errors="coerce")
            if pd.notna(x) and pd.notna(y) and pd.notna(z):
                long_rows.append({"time": t, "id": pid, "x": x, "y": y, "z": z})

    tidy = pd.DataFrame(long_rows).sort_values("time").reset_index(drop=True)
    return tidy

def filter_window(df, start, end):
    return df[(df["time"] >= pd.Timestamp(start)) & (df["time"] <= pd.Timestamp(end))]

def build_animation(dfw, window_start, window_end, fps):
    times = sorted(dfw["time"].unique())
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    ax.set_xlabel("X"); ax.set_ylabel("Y"); ax.set_zlabel("Z")
    ax.set_title(f"3D animation: {window_start.isoformat()} to {window_end.isoformat()}")

    xmin, xmax = dfw["x"].min(), dfw["x"].max()
    ymin, ymax = dfw["y"].min(), dfw["y"].max()
    zmin, zmax = dfw["z"].min(), dfw["z"].max()
    ax.set_xlim([xmin, xmax]); ax.set_ylim([ymin, ymax]); ax.set_zlim([zmin, zmax])

    ids = [0,1,2]
    lines = {pid: ax.plot([], [], [], marker=None, linestyle='-')[0] for pid in ids}
    points = {pid: ax.plot([], [], [], marker='o', linestyle='')[0] for pid in ids}

    def init():
        for pid in ids:
            lines[pid].set_data([], []); lines[pid].set_3d_properties([])
            points[pid].set_data([], []); points[pid].set_3d_properties([])
        return list(lines.values()) + list(points.values())

    def update(frame_idx):
        t = times[frame_idx]
        up_to_t = dfw[dfw["time"] <= t]
        for pid in ids:
            grp = up_to_t[up_to_t["id"] == pid]
            if grp.empty: continue
            lines[pid].set_data(grp["x"], grp["y"])
            lines[pid].set_3d_properties(grp["z"])
            last = grp.iloc[-1]
            points[pid].set_data([last["x"]], [last["y"]])
            points[pid].set_3d_properties([last["z"]])
        return list(lines.values()) + list(points.values())

    interval = int(1000 / max(1, fps))
    ani = animation.FuncAnimation(fig, update, frames=len(times),
                                  init_func=init, blit=True, interval=interval)
    return ani

def parse_time(val):
    try:
        return pd.to_datetime(val, utc=True).to_pydatetime()
    except:
        return datetime.fromtimestamp(float(val))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--window_start", type=parse_time)
    ap.add_argument("--window_end", type=parse_time)
    ap.add_argument("--mp4", help="Output MP4 path")
    ap.add_argument("--gif", help="Output GIF path")
    ap.add_argument("--fps", type=int, default=10)
    ap.add_argument("--dpi", type=int, default=150)
    args = ap.parse_args()

    df_tidy = load_data_wide(args.csv)
    if df_tidy.empty: sys.exit("No valid data.")

    if args.window_end is None:
        window_end = df_tidy["time"].max().to_pydatetime()
    else:
        window_end = args.window_end
    if args.window_start is None:
        window_start = window_end - timedelta(minutes=5)
    else:
        window_start = args.window_start

    dfw = filter_window(df_tidy, window_start, window_end)
    if dfw.empty: sys.exit("No data in 5-min window.")

    ani = build_animation(dfw, window_start, window_end, fps=args.fps)

    if args.mp4:
        ani.save(args.mp4, writer="ffmpeg", dpi=args.dpi, fps=args.fps)
        print(f"Saved MP4 to {args.mp4}")
    if args.gif:
        ani.save(args.gif, writer=animation.PillowWriter(fps=args.fps), dpi=args.dpi)
        print(f"Saved GIF to {args.gif}")

if __name__ == "__main__":
    main()
