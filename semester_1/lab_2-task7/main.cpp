#include <cmath>
#include <SFML/Graphics.hpp>

using namespace sf;

int main()
{
    int Xcoords[4], Ycoords[4], i = 0, Alpha, radius1 = 4, radius2 = 4, ycoord;
    Event event;
    RenderWindow window(VideoMode(800, 800), "Task 7");
    while (window.isOpen())
    {
        window.clear(Color(65,105,225));

        CircleShape circle1(radius1);
        circle1.setOrigin((radius1),(radius1));
        circle1.setFillColor(Color(205, 92, 92, Alpha));

        CircleShape circle2(radius2);
        circle2.setOrigin((radius2),(radius2));
        circle2.setFillColor(Color(100, 200, 92, Alpha));

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
            if (i >= 2)
                radius1 = sqrt(pow((Xcoords[0] - Xcoords[1]), 2) + pow((Ycoords[0] - Ycoords[1]), 2));
            if (i >= 4)
                radius2 = sqrt(pow((Xcoords[2]-Xcoords[3]),2) + pow((Ycoords[2]-Ycoords[3]),2));
        }

        circle1.setPosition(Xcoords[0], Ycoords[0]);
        window.draw(circle1);
        circle2.setPosition(Xcoords[2], Ycoords[2]);
        window.draw(circle2);
        window.display();
    }
    return 0;
}
