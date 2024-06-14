//За допомогою SFML, написати програму, яка за задання трьох точок буде малювати трикутник, вписані та описані кола ті їх центри



#include <cmath>
#include <SFML/Graphics.hpp>

using namespace sf;

double distance(int x1, int y1, int x2, int y2) {
    return sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2));
}

double rint(int x1, int y1, int x2, int y2, int x3, int y3){
    double AB = distance(x1, y1, x2, y2);
    double BC = distance(x2, y2, x3, y3);
    double CA = distance(x3, y3, x1, y1);
    int p = (AB+BC+CA)/2;
    double ri = ((p-AB)*(p-BC)*(p-CA))/p;
    double r = sqrt(ri);
    return (r);
}

double findCircumcenterX(int x1, int y1, int x2, int y2, int x3, int y3) {
    double circumx = 0;
    int sm1 = x1*x1 + y1*y1;
    int sm2 = x2*x2 + y2*y2;
    int sm3 = x3*x3 + y3*y3;
    int d = 2 * (x1*(y2-y3)+x2*(y3-y1)+ x3*(y1-y2));
    if(d !=0){
        circumx = (sm1*y2 + sm2*y3 + y1*sm3 - y2*sm3 - y1*sm2 - y3*sm1)/d;
    }
    return (circumx);
}
double findCircumcenterY(int x1, int y1, int x2, int y2, int x3, int y3) {
    double circumy = 0;
    int sm1 = x1*x1 + y1*y1;
    int sm2 = x2*x2 + y2*y2;
    int sm3 = x3*x3 + y3*y3;
    int d = 2 * (x1*(y2-y3)+x2*(y3-y1)+ x3*(y1-y2));
    if(d !=0) {
        circumy = -(sm1 * x2 + sm2 * x3 + x1 * sm3 - x2 * sm3 - x1 * sm2 - x3 * sm1) / d;
    }
    return (circumy);
}
double findIncenterX(int x1, int y1, int x2, int y2, int x3, int y3) {
    double AB = distance(x1, y1, x2, y2);
    double BC = distance(x2, y2, x3, y3);
    double CA = distance(x3, y3, x1, y1);

    int Incenterx = (x1 * BC + x2 * CA + x3 * AB) / (AB + BC + CA);

    return (Incenterx);
}
double findIncenterY(int x1, int y1, int x2, int y2, int x3, int y3) {
    double AB = distance(x1, y1, x2, y2);
    double BC = distance(x2, y2, x3, y3);
    double CA = distance(x3, y3, x1, y1);

    int Incentery = (y1 * BC + y2 * CA + y3 * AB) / (AB + BC + CA);

    return (Incentery);
}
int main()
{
    int Xcoords[3], Ycoords[3], i = 0, Alpha, Alpha2 = 0, circumX = 0, circumY = 0, IncenterX = 0, IncenterY = 0, rin = 1, rci = 1;
    Event event;
    RenderWindow window(VideoMode(800, 800), "Task 10");
    while (window.isOpen())
    {
        ConvexShape convex;
        convex.setPointCount(3);
        convex.setFillColor(Color(0,0,0, Alpha2));

        CircleShape IncenterCircle(rin);
        IncenterCircle.setOrigin((rin),(rin));
        IncenterCircle.setFillColor(Color::Transparent);
        IncenterCircle.setOutlineThickness(5);
        IncenterCircle.setOutlineColor(Color(173, 255, 47, Alpha2));
        CircleShape CircumCircle(rci);
        CircumCircle.setOrigin((rci),(rci));
        CircumCircle.setFillColor(Color::Transparent);
        CircumCircle.setOutlineThickness(5);
        CircumCircle.setOutlineColor(Color(255, 20, 147, Alpha2));

        CircleShape circle1(10);
        circle1.setOrigin((10),(10));
        circle1.setFillColor(Color(188, 143, 143, Alpha));
        CircleShape circle2(10);
        circle2.setOrigin((10),(10));
        circle2.setFillColor(Color(188, 143, 143, Alpha));
        CircleShape circle3(10);
        circle3.setOrigin((10),(10));
        circle3.setFillColor(Color(188, 143, 143, Alpha));

        CircleShape circumCenter(10);
        circumCenter.setOrigin((10),(10));
        circumCenter.setFillColor(Color(255, 20, 147, Alpha2));    // pink
        CircleShape inCenter(10);
        inCenter.setOrigin((10),(10));
        inCenter.setFillColor(Color(173, 255, 47, Alpha2)); //green

        while (window.pollEvent(event))
        {
            if (event.type == Event::Closed)
                window.close();
            if (event.type == Event::MouseButtonPressed){
                Xcoords[i] = event.mouseButton.x;
                Ycoords[i] = event.mouseButton.y;
                i++;
                Alpha = 1000;
            }
            if (i>2)
                Alpha2 = 1000;
                circumX = findCircumcenterX(Xcoords[0], Ycoords[0],Xcoords[1], Ycoords[1],Xcoords[2], Ycoords[2]);
                circumY = findCircumcenterY(Xcoords[0], Ycoords[0],Xcoords[1], Ycoords[1],Xcoords[2], Ycoords[2]);
                IncenterX = findIncenterX(Xcoords[0], Ycoords[0],Xcoords[1], Ycoords[1],Xcoords[2], Ycoords[2]);
                IncenterY = findIncenterY(Xcoords[0], Ycoords[0],Xcoords[1], Ycoords[1],Xcoords[2], Ycoords[2]);
                rci = distance(Xcoords[0], Ycoords[0], circumX, circumY);
                rin = rint(Xcoords[0], Ycoords[0],Xcoords[1], Ycoords[1],Xcoords[2], Ycoords[2]);
        }

        convex.setPoint(0, Vector2f(Xcoords[0], Ycoords[0]));
        convex.setPoint(1, Vector2f(Xcoords[1], Ycoords[1]));
        convex.setPoint(2, Vector2f(Xcoords[2], Ycoords[2]));

        circle1.setPosition(Xcoords[0], Ycoords[0]);
        circle2.setPosition(Xcoords[1], Ycoords[1]);
        circle3.setPosition(Xcoords[2], Ycoords[2]);


        inCenter.setPosition(IncenterX,IncenterY);
        circumCenter.setPosition(circumX, circumY);

        IncenterCircle.setPosition(IncenterX,IncenterY);
        CircumCircle.setPosition(circumX, circumY);

        window.draw(circle1);
        window.draw(circle2);
        window.draw(circle3);
        window.draw(convex);
        window.draw(circumCenter);
        window.draw(inCenter);
        window.draw(IncenterCircle);
        window.draw(CircumCircle);

        window.display();

        window.clear(Color(100, 149, 237));
    }
    return 0;
}
