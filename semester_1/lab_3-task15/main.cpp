// апроксимація заданної функції

#include <iostream>
#include <cmath>
using namespace std;
const double NMax = 3;          //выбор верхнего предела отрезка
const double NMin = -3;            //Выбор нижнего предела отрезка
const double otstup = 0.1;        //Отступ для апроксимации
const double Nser = ((NMax - NMin)/otstup) + 1;

double f(double x){
    return cos(x);                 // вместо log(x) вводите нужную для апроксимации функцию
}

void yoffunction( double arr[])
{
    int i = 0;
    for (double x = NMin; x <= NMax; x+=otstup){
        arr[i] = f(x);
        i++;
        }
}

pair<double, double> aandb(double yarr[]){
    double xysum =0, xsum=0, ysum=0, xsqsum=0, a, b;
    int i = 0;
    for (double x = NMin; x<=NMax; x+=otstup){

        xysum+=x*yarr[i];
        xsum+=x;
        ysum+=yarr[i];
        xsqsum+=x*x;
        i++;
    }
    a = (Nser*xysum - ysum*xsum)/(Nser*xsqsum - xsum*xsum);
    b = (ysum - a*xsum)/(Nser);
    return pair<double,double>(a,b);
}
int main() {
    double arr[(int)Nser];
    yoffunction(arr);
    auto p = aandb(arr);
    cout << "y = " << p.first << "x + " << p.second <<endl;
    return 0;
}
