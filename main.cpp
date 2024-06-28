//
//  main.cpp
//  Perceptor
//
//  Created by Daniel Mulangu on 11/5/20.
//  Copyright © 2020 Daniel Mulangu. All rights reserved.
//

#include <iostream>
#include<string.h>
using namespace std;
struct car{
    float price;
    char name;
    int rent=0;
    float amount=0;
    char type[5];
    char plate[10];
};
void set_renting(struct car d);
void unset_renting(struct car d);
void set_price(struct car d);
void percept(struct car d);
void set_plate(struct car d);
void set_type(struct car d);

int main()
{
    struct car x[10];
    for(int i=0;i<3;i++)
    {
        set_renting(x[i]);
    }
    // show available cars
    for(int i=0;i<10;i++)
    {
        if(x[i].rent==0)
        {
            cout<<endl<<"Plate "<<x[i].plate<<"Type "<<x[i].type<<"Price "<<x[i].price;
        }
    }
    
    return 0;
}

void set_renting(struct car d)
{
    cout<<"Enter name of the renter";
    gets(d.name);
    d.rent=1;
    cout<<"Renter entered successfully";
}

void set_price(struct car d)
{
    float x;
    cout<<"Enter the price of the car";
    cin>>x;
    d.price=x;
    cout<<"Price entered successfully";
}
void unset_renting(struct car d)
{
    d.rent=0;
    cout<<"Done successfully";
}
void percept(struct car d)
{
    float y;
    cout<<"Enter the price of the car";
    cin>>y;
    d.amount+=y;
}

void set_type(struct car d)
{
    cout<<"Enter the type of the car";
    gets(d.type);
    cout<<"Type set succesffully";
}

void set_plate(struct car d)
{
    cout<< "Enter the plate number of the car";
    gets(d.plate);
    cout<<"Plate entered succesffully";
}
