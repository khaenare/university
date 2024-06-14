// перевірка чи задовільняє строка мастці,
// Символ '?' в масці відповідає будь-якому одиночному символу у рядку.
// Символ '*' в масці відповідає будь-якій послідовності символів у рядку.

#include <iostream>
#include <string>
using namespace std;

bool isMatch(string str, string mask) {
    int strLenght = str.length();
    int currSlock = 0, currMlock = 0, lastStar = -1, matchPos = -1;

    while (currSlock < strLenght) {
        if (mask[currMlock] == '?' || str[currSlock] == mask[currMlock]) {
            currSlock++;
            currMlock++;
            lastStar = -1;
            matchPos = -1;
        }
        else if (mask[currMlock] == '*') {
            lastStar = currMlock;
            matchPos = currSlock;
            currMlock++;
        }
        else if (lastStar != -1) {
            currMlock = lastStar + 1;
            currSlock = ++matchPos;
        }
        else {
            return false;
        }
    }

    return true;
}

int main() {
    string str = "";
    cin >> str;
    string mask = "";
    cin >> mask;

    if (isMatch(str, mask)) {
        cout << "Zadovil'niae Mastci" << endl;
    } else {
        cout << "Ne zadovil'niae Mastci" << endl;
    }

    return 0;
}
