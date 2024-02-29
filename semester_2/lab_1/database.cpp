/*
Інформація про монстрів у комп’ютерній грі. Зберігаються наступні дані про кожного монстра:
ім’я; кількість одиниць здоров’я (ціле число, не більше 50000); кількість одиниць атаки (ціле число, не більше 2000);
шанс виконати спеціальну атаку (дійсне число від 0 до 1); дата та час появи у грі;
тип спеціальної атаки – збільшити пошкодження, повторити атаку, вилікувати себе, паралізувати супротивника;
---------------------------------------------------------------------------------------------------------------------
Критерії пошуку:
 1) Монстри з іменем, що містить заданий фрагмент тексту;
 2) Монстри з кількістю одиниць здоров’я не менше заданого та кількістю одиниць атаки не більше заданого;
 3) Монстри із заданим типом спеціальної атаки, що з’явились у грі не пізніше заданого часу;
*/


#include <iostream>
#include <fstream>
#include <vector>
#include <string>
using namespace std;

struct Date{
    int hour;
    int minute;
    int day;
    int month;
    int year;
};
struct Monster {
    string name;
    int health;
    int attack;
    double specialAttackChance;
    string specialAttackType;
    Date spawn;
};

void addMonster(vector<Monster>& database);
void storeAsText(const vector<Monster>& database);
void storeAsBinary(const vector<Monster>& database);
void retrieveFromText(vector<Monster>& database);
void retrieveFromBinary(vector<Monster>& database);
void displayAll(const vector<Monster>& database);
void search(const vector<Monster>& database);


int main() {
    vector<Monster> database;
    int choice;

    do {
        cout << "\n1. Add Monster\n"                    // Додавання монстра в векторний  массив монстра
                "2. Store Data (Text)\n"                // Копіювання всіх монстрів з векторного массива в Txt файл для подальшого збереження
                "3. Store Data (Binary)\n"              // Копіювання всіх монстрів з векторного массива в Bin файл для подальшого збереження
                "4. Retrieve Data (Text)\n"             // Копіювання всіх монстрів з Txt файлу в векторний массив
                "5. Retrieve Data (Binary)\n"           // Копіювання всіх монстрів з Bin файлу в векторний массив
                "6. Display All\n"                      // Виведення всіх монстрів
                "7. Search\n"                           // Режим пошуку
                "8. Exit\n"                             // Вихід з програми
                "Enter your choice: ";
        cin >> choice;

        switch (choice) {
            case 1:
                addMonster(database);
                break;
            case 2:
                storeAsText(database);
                break;
            case 3:
                storeAsBinary(database);
                break;
            case 4:
                retrieveFromText(database);
                break;
            case 5:
                retrieveFromBinary(database);
                break;
            case 6:
                displayAll(database);
                break;
            case 7:
                search(database);
                break;
            case 8:
                cout << "Exiting program.\n";
                break;
            default:
                cout << "Invalid choice. Please try again.\n";
                break;
        }
    } while (choice != 8);

    return 0;
}

void addMonster(vector<Monster>& database) {
    Monster newMonster;
    cout << "Enter monster name: ";
    cin >> newMonster.name;
    cout << "Enter number of health units: ";
    cin >> newMonster.health;
    cout << "Enter number of attack units: ";
    cin >> newMonster.attack;
    cout << "Enter chance to perform a special attack (0 to 1): ";
    cin >> newMonster.specialAttackChance;
    cout << "Enter type of special attack: ";
    cin >> newMonster.specialAttackType;
    cout << "Enter hour: ";
    cin >> newMonster.spawn.hour;
    cout << "Enter minute: ";
    cin >> newMonster.spawn.minute;
    cout << "Enter day: ";
    cin >> newMonster.spawn.day;
    cout << "Enter month: ";
    cin >> newMonster.spawn.month;
    cout << "Enter year: ";
    cin >> newMonster.spawn.year;
    database.push_back(newMonster);
    cout << "Monster added successfully.\n";
}

void storeAsText(const vector<Monster>& database) {
    ofstream outFile("monsters.txt");
    if (!outFile.is_open()) {
        cout << "Error opening file for writing.\n";
        return;
    }

    for (const auto& monster : database) {
        outFile << monster.name << " "
                << monster.health << " "
                << monster.attack << " "
                << monster.specialAttackChance << " "
                << monster.specialAttackType << " "
                << monster.spawn.hour << " "
                << monster.spawn.minute << " "
                << monster.spawn.day << " "
                << monster.spawn.month << " "
                << monster.spawn.year << endl;
    }
    cout << "Data stored as text successfully.\n";
    outFile.close();
}

void storeAsBinary(const vector<Monster>& database) {
    ofstream outFile("monsters.bin", ios::binary);
    if (!outFile.is_open()) {
        cout << "Error opening file for writing.\n";
        return;
    }

    size_t size = database.size();
    outFile.write(reinterpret_cast<const char*>(&size), sizeof(size_t));
    for (const auto& monster : database) {
        size_t nameSize = monster.name.size();
        outFile.write(reinterpret_cast<const char*>(&nameSize), sizeof(size_t));
        outFile.write(monster.name.c_str(), nameSize);
        outFile.write(reinterpret_cast<const char*>(&monster.health), sizeof(int));
        outFile.write(reinterpret_cast<const char*>(&monster.attack), sizeof(int));
        outFile.write(reinterpret_cast<const char*>(&monster.specialAttackChance), sizeof(double));
        size_t typeSize = monster.specialAttackType.size();
        outFile.write(reinterpret_cast<const char*>(&typeSize), sizeof(size_t));
        outFile.write(monster.specialAttackType.c_str(), typeSize);
        outFile.write(reinterpret_cast<const char*>(&monster.spawn.hour), sizeof(int));
        outFile.write(reinterpret_cast<const char*>(&monster.spawn.minute), sizeof(int));
        outFile.write(reinterpret_cast<const char*>(&monster.spawn.day), sizeof(int));
        outFile.write(reinterpret_cast<const char*>(&monster.spawn.minute), sizeof(int));
        outFile.write(reinterpret_cast<const char*>(&monster.spawn.year), sizeof(int));
    }
    cout << "Data stored as binary successfully.\n";
    outFile.close();
}

void retrieveFromText(vector<Monster>& database) {
    ifstream inFile("monsters.txt");
    if (!inFile.is_open()) {
        cout << "Error opening file for reading.\n";
        return;
    }

    Monster monster;
    while (inFile >> monster.name >> monster.health >> monster.attack >> monster.specialAttackChance
                  >> monster.specialAttackType >> monster.spawn.hour >> monster.spawn.minute >> monster.spawn.day >> monster.spawn.month >> monster.spawn.year ) {
        database.push_back(monster);
    }
    cout << "Data retrieved from text successfully.\n";
    inFile.close();
}

void retrieveFromBinary(vector<Monster>& database) {
    ifstream inFile("monsters.bin", ios::binary);
    if (!inFile.is_open()) {
        cout << "Error opening file for reading.\n";
        return;
    }

    size_t size;
    inFile.read(reinterpret_cast<char*>(&size), sizeof(size_t));
    database.resize(size);

    for (auto& monster : database) {
        size_t nameSize, typeSize;
        inFile.read(reinterpret_cast<char*>(&nameSize), sizeof(size_t));
        monster.name.resize(nameSize);
        inFile.read(&monster.name[0], nameSize);
        inFile.read(reinterpret_cast<char*>(&monster.health), sizeof(int));
        inFile.read(reinterpret_cast<char*>(&monster.attack), sizeof(int));
        inFile.read(reinterpret_cast<char*>(&monster.specialAttackChance), sizeof(double));
        inFile.read(reinterpret_cast<char*>(&typeSize), sizeof(size_t));
        monster.specialAttackType.resize(typeSize);
        inFile.read(&monster.specialAttackType[0], typeSize);
        inFile.read(reinterpret_cast<char*>(&monster.spawn.hour), sizeof(int));
        inFile.read(reinterpret_cast<char*>(&monster.spawn.minute), sizeof(int));
        inFile.read(reinterpret_cast<char*>(&monster.spawn.day), sizeof(int));
        inFile.read(reinterpret_cast<char*>(&monster.spawn.month), sizeof(int));
        inFile.read(reinterpret_cast<char*>(&monster.spawn.year), sizeof(int));
    }
    cout << "Data retrieved from binary successfully.\n";
    inFile.close();
}

void displayAll(const vector<Monster>& database) {
    if (database.empty()) {
        cout << "Database is empty.\n";
        return;
    }

    cout << "Monsters in the database:\n";
    for (const auto& monster : database) {
        cout <<
        "Name: "                            << monster.name << "\n"
        "Health: "                          << monster.health << "\n"
        "Attack: "                          << monster.attack << "\n"
        "Special Attack Chance: "           << monster.specialAttackChance << "\n"
        "Special Attack Type: "             << monster.specialAttackType << "\n"
        "Appearance Time: "                 << monster.spawn.hour << ":" << monster.spawn.minute << " "
                                            << monster.spawn.day << "." << monster.spawn.month << "." << monster.spawn.year << "\n\n";
    }
}

void search(const vector<Monster>& database) {
    string searchText;
    cout << "Enter text to search in monster names: ";
    cin >> searchText;

    for (const auto& monster : database) {
        if (monster.name.find(searchText) != string::npos) {
            cout << "\n" <<
            "Name: "                        << monster.name << "\n"
            "Health: "                      << monster.health << "\n"
            "Attack: "                      << monster.attack << "\n"
            "Special Attack Chance: "       << monster.specialAttackChance << "\n"
            "Special Attack Type: "         << monster.specialAttackType << "\n"
            "Appearance Time: "             << monster.spawn.hour << ":" << monster.spawn.minute << " "
                                            << monster.spawn.day << "." << monster.spawn.month << "." << monster.spawn.year << "\n\n";
        }else cout << "Monsters don`t found ";
    }
}
