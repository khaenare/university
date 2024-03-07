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
#include <chrono>
#include <random>
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
struct Monster generateRandomMonster() {
    return Monster{"Monster", rand() % 50001, rand() % 2001,
                   static_cast<double>(rand()) / RAND_MAX, "IncAtk", {0, 0, 1, 1, 2020}};
}

void addMonster(vector<Monster>& database);
void addMonsterBench(vector<Monster>& buffer, Monster Monster);
void storeAsText(const vector<Monster>& database, const string& filePath);
void storeAsBinary(const vector<Monster>& database, const string& filePath);
void retrieveFromText(vector<Monster>& database, const string& filePath);
void retrieveFromBinary(vector<Monster> &database, const string& filePath);
void clearFileData();
void displayAll(const vector<Monster>& database);
void searchByName(const vector<Monster>& database);
void searchByHealthAndAttack(const vector<Monster>& database);
void searchBySpecialAttackTypeAndTime(const vector<Monster>& database);
void basicMode(vector<Monster>& database);
void benchmarkMode();


int main() {
    vector<Monster> database;
    int mode;
    cout << "Please, select a number of mode:\n1. Basic Mode\n2. Demonstration mode \n3. Benchmark mode:\nEnter a number of database: ";
    cin >> mode;

    switch (mode) {
        case 1:
            basicMode(database);
            break;
        case 2:
            //demonstrationMode();
            break;
        case 3:
            benchmarkMode();
            break;
        default:
            cerr << "Error! You enter incoretct mode\n";
            break;
    }
    return 0;
}

void basicMode(vector<Monster>& database){
    int choice1, choice2;

    do {
        cout << "\n1. Add Monster\n"                    // Додавання монстра в векторний  массив монстра
                "2. Store Data (Text)\n"                // Копіювання всіх монстрів з векторного массива в Txt файл для подальшого збереження
                "3. Store Data (Binary)\n"              // Копіювання всіх монстрів з векторного массива в Bin файл для подальшого збереження
                "4. Retrieve Data (Text)\n"             // Копіювання всіх монстрів з Txt файлу в векторний массив
                "5. Retrieve Data (Binary)\n"           // Копіювання всіх монстрів з Bin файлу в векторний массив
                "6. Clean Data\n"                       // "костиль" для видалення та очистки всіх данних з Txt файлу
                "7. Display All\n"                      // Виведення всіх монстрів
                "8. Search\n"                           // Режим пошуку
                "9. Exit\n"                            // Вихід з програми
                "Enter your choice: ";
        cin >> choice1;

        switch (choice1) {
            case 1:
                addMonster(database);
                break;
            case 2:
                storeAsText(database, "monsters.txt");
                break;
            case 3:
                storeAsBinary(database, "monsters.bin");
                break;
            case 4:
                retrieveFromText(database, "monsters.txt");
                break;
            case 5:
                retrieveFromBinary(database, "monsters.bin");
                break;
            case 6:
                clearFileData();
                break;
            case 7:
                displayAll(database);
                break;
            case 8:
                cout << "Chose type of search: \n"
                        "1. By name \n"
                        "2. By hp and atc \n"
                        "3. By time and attack type\n";
                cin >> choice2;
                switch (choice2) {
                    case 1:
                        searchByName(database);
                        break;
                    case 2:
                        searchByHealthAndAttack(database);
                        break;
                    case 3:
                        searchBySpecialAttackTypeAndTime(database);
                        break;
                    default:
                        cout << "Invalid choice. Please try again.\n";
                        break;
                }

                break;
            case 9:
                cout << "Exiting program.\n";
                break;
            default:
                cout << "Invalid choice. Please try again.\n";
                break;
        }
    } while (choice1 != 9);
}

void benchmarkMode() {
    cout << "\n=== Benchmark mode ===\n";

    string txtFilename = "monstersbench.txt";
    string binFilename = "monstersbench.bin";

    int num;
    cout << "Enter a number of elements for database: ";
    cin >> num;
    if (num < 1) {
        cout << "Number of elements must be greater than 0.\n";
        return;
    }

    for (int mode = 2; mode >= 0; mode--) {
        vector<Monster> buffer;
        string operationMode;
        if (mode == 2) operationMode = "TXT DATABASE";
        else if (mode == 1) operationMode = "BIN DATABASE";
        else operationMode = "VECTOR DATABASE";

        cout << "\n=== START BENCHMARK FOR " << operationMode << " ===\n";

        // Бенчмарк для додавання монстрів
        auto startTime = chrono::high_resolution_clock::now();
        for (int i = 0; i < num; i++) {
            // Припустимо, що є функція для генерації випадкового монстра
            Monster newMonster = generateRandomMonster();
            addMonsterBench(buffer, newMonster);
        }
        auto endTime = chrono::high_resolution_clock::now();

        // Бенчмарк для збереження та відновлення даних
        if (mode != 0) {
            if (mode == 2) {
                storeAsText(buffer, txtFilename);
                buffer.clear();
                retrieveFromText(buffer, txtFilename);
            } else {
                storeAsBinary(buffer, binFilename);
                buffer.clear();
                retrieveFromBinary(buffer, binFilename);
            }
        }

        auto duration = chrono::duration_cast<chrono::milliseconds>(endTime - startTime).count();
        cout << "Total time for " << operationMode << ": " << duration << " ms\n";
    }
}


void addMonster(vector<Monster>& database) {
    Monster newMonster;
    cout << "Enter monster name: ";
    cin >> newMonster.name;

    cout << "Enter number of health: ";
    while (!(cin >> newMonster.health) || newMonster.health < 0 || newMonster.health > 50000) {
        cout << "Invalid input. Please enter a number between 0 and 50000: ";
        cin.clear();
    }

    cout << "Enter number of attack units: ";
    while (!(cin >> newMonster.attack) || newMonster.attack < 0 || newMonster.attack > 2000) {
        cout << "Invalid input. Please enter a number between 0 and 2000: ";
        cin.clear();
    }

    cout << "Enter chance to perform a special attack (0 to 1): ";
    while (!(cin >> newMonster.specialAttackChance) || newMonster.specialAttackChance < 0 || newMonster.specialAttackChance > 1) {
        cout << "Invalid input. Please enter a number between 0 and 1: ";
        cin.clear();
    }

    cout << "Enter type of special attack (IncAtk, RepAtk, Heal, Stan): ";
    cin >> newMonster.specialAttackType;
    while (newMonster.specialAttackType != "IncAtk" && newMonster.specialAttackType != "RepAtk" && newMonster.specialAttackType != "Heal" && newMonster.specialAttackType != "Stan") {
        cout << "Invalid input. Please enter one of the following: IncAtk, RepAtk, Heal, Stan: ";
        cin >> newMonster.specialAttackType;
    }

    cout << "Enter hour of spawn: ";
    cin >> newMonster.spawn.hour;
    cout << "Enter minute of spawn: ";
    cin >> newMonster.spawn.minute;
    cout << "Enter day of spawn: ";
    cin >> newMonster.spawn.day;
    cout << "Enter month of spawn: ";
    cin >> newMonster.spawn.month;
    cout << "Enter year of spawn: ";
    cin >> newMonster.spawn.year;

    database.push_back(newMonster);
    cout << "Monster added successfully.\n";
}

void addMonsterBench(vector<Monster>& buffer, Monster generatedMonster){
    buffer.push_back(generatedMonster);
}

void storeAsText(const vector<Monster>& database, const string& filePath) {
    ofstream outFile(filePath);
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

void storeAsBinary(const vector<Monster>& database, const string& filePath) {
    ofstream outFile(filePath, ios::binary);
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
        outFile.write(reinterpret_cast<const char*>(&monster.spawn.month), sizeof(int));
        outFile.write(reinterpret_cast<const char*>(&monster.spawn.year), sizeof(int));
    }
    cout << "Data stored as binary successfully.\n";
    outFile.close();
}

void retrieveFromText(vector<Monster>& database, const string& filePath) {
    ifstream inFile(filePath);
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

void retrieveFromBinary(vector<Monster> &database, const string& filePath) {                                //P.S: ненавиджу бінарні файли...
    ifstream inFile(filePath, ios::binary);
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

void clearFileData() {
    int fileChoice;
    cout << "Choose the file to clear:\n"
         << "1. Text file\n"
         << "2. Binary file\n";
    cin >> fileChoice;

    string fileName;
    ios_base::openmode mode = ios::out;

    switch (fileChoice) {
        case 1:
            fileName = "monsters.txt";
            break;
        case 2:
            fileName = "monsters.bin";
            mode |= ios::binary; // додаємо mode для бінарного файлу
            break;
        default:
            cout << "Invalid choice. Exiting function.\n";
            return;
    }
    ofstream file(fileName, mode | ios::trunc);
    file.close();
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

void searchByName(const vector<Monster>& database) {
    string searchText;
    cout << "Enter text to searchByName in monster names: ";
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

void searchByHealthAndAttack(const vector<Monster>& database) {
    int maxAttack, minHealth;
    cout << "Enter Max Attack and Min Health\n";
    cin >> maxAttack >> minHealth;
    for (const auto &monster: database) {
        if (monster.health >= minHealth && monster.attack <= maxAttack) {
            cout << "\n" <<
                 "Name: "                       << monster.name << "\n"
                 "Health: "                     << monster.health << "\n"
                 "Attack: "                     << monster.attack << "\n"
                 "Special Attack Chance: "      << monster.specialAttackChance << "\n"
                 "Special Attack Type: "        << monster.specialAttackType << "\n"
                 "Appearance Time: "            << monster.spawn.hour << ":" << monster.spawn.minute << " "
                                                << monster.spawn.day << "." << monster.spawn.month << "." << monster.spawn.year << "\n\n";
        } else cout << "Monsters don`t found " << "\n";
    }
}

void searchBySpecialAttackTypeAndTime(const vector<Monster>& database) {
    bool found = false;

    string specialAttackType;
    Date untilDate;
    cout << "Enter type of special attack (IncAtk, RepAtk, Heal, Stan): ";
    cin >> specialAttackType;
    cout << "Enter latest date (hour, minute,day, month, year): \n";
    cin >> untilDate.hour >> untilDate.minute >> untilDate.day >> untilDate.month >> untilDate.year;

    for (const auto& monster : database) {
        if (monster.specialAttackType == specialAttackType &&
            (monster.spawn.year < untilDate.year ||
             (monster.spawn.year == untilDate.year && monster.spawn.month < untilDate.month) ||
             (monster.spawn.year == untilDate.year && monster.spawn.month == untilDate.month && monster.spawn.day <= untilDate.day) ||
             (monster.spawn.year == untilDate.year && monster.spawn.month == untilDate.month && monster.spawn.day == untilDate.day && monster.spawn.hour <= untilDate.hour) ||
             (monster.spawn.year == untilDate.year && monster.spawn.month == untilDate.month && monster.spawn.day == untilDate.day && monster.spawn.hour == untilDate.hour && monster.spawn.minute <= untilDate.minute))) {
            cout << "\n" <<
                 "Name: "                       << monster.name << "\n"
                 "Health: "                     << monster.health << "\n"
                 "Attack: "                     << monster.attack << "\n"
                 "Special Attack Chance: "      << monster.specialAttackChance << "\n"
                 "Special Attack Type: "        << monster.specialAttackType << "\n"
                 "Appearance Time: "            << monster.spawn.hour << ":" << monster.spawn.minute << " "
                                                << monster.spawn.day << "." << monster.spawn.month << "." << monster.spawn.year << "\n\n";
            found = true;
        }
    }
    if (!found) {
        cout << "No monsters found matching the criteria.\n";
    }
}
