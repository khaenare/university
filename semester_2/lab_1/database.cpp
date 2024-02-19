/*
Інформація про товари в магазині. Зберігаються наступні дані про кожен товар: назва товару; 
одиниці виміру – кілограми, літри, поштучно, пакунки; кількість товару (у відповідних одиницях, дійсне число); 
дата та час виробництва; термін зберігання (кількість діб з дати виробництва, не більше 10 років). Критерії пошуку:
1) Товари з назвою, що починається із заданого фрагменту тексту; 
2) Tовари із заданим діапазоном кількості у заданій одиниці вимірювання; 
3) Tовари з датою виробництва не пізніше заданої.
*/
#include <iostream>
#include <string>
#include <fstream>
#include <vector>
#include <cstdlib>
#include <ctime>
#include <chrono>
#include <thread>

#define txtDatabse true
#define generateRandomElem true
#define benchmark true
#define findName true
#define findNumOfUnit true
#define findDate true
#define ZeroValue 0

using namespace std;

//Функція для перевірки правильності введення даних користувачем
template <typename T>
T getValidInput(const string& prompt) {
    T value;
    bool cinFail;
    do
    {
        cinFail = false;
        cout << prompt;
        cin >> value;
        if (cin.fail()) {
            cerr << "\n### Invalid input. Please enter a valid number. ###\n\n";
            cin.clear();
            cin.ignore(numeric_limits<streamsize>::max(), '\n');
            cinFail = true;
        };
    } while (cinFail);
    return value;
}

//Структури
struct date
{
    int year, month, day, hour, minute, second;

    date(int year = int(), int month = int(), int day = int(), int hour = int(), int minute = int(), int second = int())
    {
        this->year = year;
        this->month = month;
        this->day = day;
        this->hour = hour;
        this->minute = minute;
        this->second = second;
    }

    date addDaysToDate(int days)
    {
        date resultDate = *this;
        while (days > 0)
        {
            int daysInCurrentMonth = resultDate.dayInMonth(resultDate.month);
            if (days <= daysInCurrentMonth - resultDate.day)
            {
                resultDate.day += days;
                days = 0;
            }
            else
            {
                days -= (daysInCurrentMonth - resultDate.day + 1);
                resultDate.day = 1;
                resultDate.month += 1;
                if (resultDate.month > 12)
                {
                    resultDate.month = 1;
                    resultDate.year += 1;
                }
            }
        }
        return resultDate;
    }
    int dayInMonth(int month)
    {
        switch (month)
        {
        case 1: case 3: case 5: case 7: case 8: case 10: case 12:
            return 31;
        case 4: case 6: case 9: case 11:
            return 30;
        case 2:
            return (year % 4 == 0 && (year % 100 != 0 || year % 400 == 0)) ? 29 : 28;
        default:
            return -1;  // Повертаємо -1 у випадку некоректного місяця
        }
    }
    void getDate()     //Функція запиту дати від користувача та перевірка кожного значення на правилність введення
    {
        do { this->year = getValidInput<int>("Enter year: "); } while (this->year < 2015);
        do { this->month = getValidInput<int>("Enter month: "); } while (this->month > 12 || this->month < 1);
        do { this->day = getValidInput<int>("Enter day: "); } while (this->day > dayInMonth(this->month) || this->day < 1);
        do { this->hour = getValidInput<int>("Enter hour: "); } while (this->hour > 24 || this->hour < 0);
        do { this->minute = getValidInput<int>("Enter minute: "); } while (this->minute > 59 || this->minute < 0);
        do { this->second = getValidInput<int>("Enter second: "); } while (this->second > 59 || this->second < 0);
    }
    void printDate() { cout << this->year << "." << this->month << "." << this->day << "\n"; }
    void printTime() { cout << this->hour << ":" << this->minute << ":" << this->second << "\n"; }

    bool operator>(const date& other)
    {
        if (this->year > other.year) return true;
        else if (this->year < other.year) return false;

        if (this->month > other.month) return true;
        else if (this->month < other.month) return false;

        if (this->day > other.day) return true;
        else if (this->day < other.day) return false;

        if (this->hour > other.hour) return true;
        else if (this->hour < other.hour) return false;

        if (this->minute > other.minute) return true;
        else if (this->minute < other.minute) return false;

        return this->second > other.second;
    }
};
struct Product
{
    int id, shelf_life;
    string name, unit;
    double quantity;
    date production_date, shelf_time_date;

    void getInfo() //Функція для отримання данних про товар від користувача
    {
        this->name = getValidInput<string>("Enter name: ");
        do { this->unit = getValidInput<string>("Enter unit: "); } while (this->unit != "kg" && this->unit != "liter" && this->unit != "package" && this->unit != "piece");
        do { this->quantity = getValidInput<double>("Enter quantity: "); } while (this->quantity < 0);
        production_date.getDate();
        do { this->shelf_life = getValidInput<int>("Enter shelf life(in days. Less than 10 years): "); } while (this->shelf_life < 0 || this->shelf_life > 3660);
    }

    void printInfo() //Функція для виведення данних про товар для користувача
    {
        cout << "=====================\n";
        cout << "Id: " << this->id << "\n";
        cout << "Product: " << this->name << "\n";
        cout << "Unit: " << this->unit << "\n";
        cout << "Quantity: " << this->quantity << "\n";
        cout << "Production date: "; production_date.printDate();
        cout << "Production time: "; production_date.printTime();
        cout << "Shelf time: "; production_date.addDaysToDate(shelf_life).printDate();
        cout << "=====================\n";
    }
};

void DatabaseManagement(const string& filename, bool isTxtDatabase);
void VectorDatabase();
void benchmarkMode();
void demonstrationMode();

void addElement(vector<Product>& bufferDatabase, bool randomElement, bool isBenchmark);
void recordDatabase(const string& filename, const vector<Product>& bufferDatabase, bool isTxtDatabase, bool isBenchmark);
void restore(const string& filename, vector<Product>& database, bool isTxtDatabase, bool isBenchmark);
void readAllDatabase(vector<Product>& bufferDatabase);
void searchElementsManage(vector<Product>& bufferDatabase);
vector<Product> search(vector<Product> bufferDatabase, bool name, string fragment, bool numOfUnit, double diaposoneStart, double diaposoneEnd, bool checkDate, date startDate);
void modifyElement(vector<Product>& bufferDatabase);
void delElement(vector<Product>& bufferDatabase);

Product generateRandomElement();
string generateString(int len);
date getRandomDate();

int main()
{
    srand(time(nullptr));
    cout << "\n--- Database loaded successfully! ---\n";
    int mode;
    string filename;
    mode = getValidInput<int>("Please, select a number of mode:\n1. Database management\n2. Demonstration mode \n3. Benchmark mode:\nEnter a number of database: ");

    switch (mode)
    {
    case 1:
        int modeManagement;
        modeManagement = getValidInput<int>("\nPlease, select a number of database:\n1. Vector Database \n2. TXT File Database\n3. Bin File Database\nEnter a number of database: ");;
        switch (modeManagement)
        {
        case 1:
            VectorDatabase();
            break;
        case 2:
            filename = "database.txt";
            DatabaseManagement(filename, txtDatabse);
            break;
        case 3:
            filename = "database.bin";
            DatabaseManagement(filename, !txtDatabse);
            break;
        default:
            cerr << "Error! You choised incorrect database\n";
            break;
        }
        break;
    case 2:
        demonstrationMode();
        break;
    case 3:
        benchmarkMode();
        break;
    default:
        cerr << "Error! You enter incoretct mode\n";
        break;
    }
}

void DatabaseManagement(const string& filename, bool isTxtDatabse)
{
    ios_base::openmode fileMode = isTxtDatabse ? ios::app : ios::app | ios::binary ;
    fstream outputFile(filename, fileMode);

    if (!outputFile.is_open())
    {
        cerr << "\n### Error opening the file " << filename << ". ###\n";
        return;
    }

    bool manage = true;
    vector<Product> bufferDatabase; //Масив для збереження тимчасових елементів
    restore(filename, bufferDatabase, isTxtDatabse, !benchmark);

    cout << "\nHere you can manage the text database.\n";
    while (manage)
    {
        cout << "Please select a operation: \n"
                "1. Add an element to the database buffer\n"
                "2. Record database to the file\n"
                "3. Restore database to the database buffer\n"
                "4. Print the database\n"
                "5. Search an element in database by criterias\n"
                "6. Modify an element in the database\n"
                "7. Delete all database buffet or delete an element in database buffer\n"
                "0. Exit\n";
        int operation;
        operation = getValidInput<int>("Please enter a number of operation: ");

        switch (operation)
        {
        case 0:
            manage = false;
            break;
        case 1:
            addElement(bufferDatabase, generateRandomElem, !benchmark);
            break;
        case 2:
            recordDatabase(filename, bufferDatabase, isTxtDatabse, !benchmark);
            break;
        case 3:
            restore(filename, bufferDatabase, isTxtDatabse, !benchmark);
            break;
        case 4:
            readAllDatabase(bufferDatabase);
            break;
        case 5:
            searchElementsManage(bufferDatabase);
            break;
        case 6:
            modifyElement(bufferDatabase);
            break;
        case 7:
            delElement(bufferDatabase);
            break;
        default:
            cerr << "\n### Error! You enter incorect mode! ###\n";
            break;
        }
    }

    cout << "\n=== Text database file '" << filename << "' has been created/updated! ===\n";
    outputFile.close();
}
void VectorDatabase()
{
    bool manage = true;
    vector<Product> bufferDatabase, Database, copyDatabase; //Масив для збереження тимчасових елементів

    while (manage)
    {
        cout << "\nHere you can manage the text database. Please select a operation: \n";
        cout << "0. Exit\n1. Add element to database\n2. Record date to file\n3. Restore database\n4. Output database\n5. Searh for an product by criteria\n6. Modify an element\n7. Delete database or element\n";
        int operation;
        operation = getValidInput<int>("Please enter a number of operation: ");

        switch (operation)
        {
        case 0:
            manage = false;
            break;
        case 1:
            addElement(bufferDatabase, false, false);
            break;
        case 2:
            Database = bufferDatabase;
            break;
        case 3:
            int record;
            record = getValidInput<int>("\n1. Create copy\n2. restore copy");
            if (record == 1) copyDatabase = Database;
            else if (record == 2) Database = copyDatabase;
            else cout << "\n### You enter incorect number! ###\n";
            break;
        case 4:
            readAllDatabase(bufferDatabase);
            break;
        case 5:
            searchElementsManage(bufferDatabase);
            break;
        case 6:
            modifyElement(bufferDatabase);
            break;
        case 7:
            delElement(bufferDatabase);
            break;
        default:
            cerr << "Error! You enter incoretct mode\n";
            break;
        }
    }

    cout << "\n=== Vector Database has been deleted. ===\n";
}
void demonstrationMode()
{
    bool manage = true;
    date zeroValueDate(0, 0, 0, 0, 0, 0);
    vector<Product> bufferDatabase, demonstrationDatabase; // Масив для збереження тимчасових елементів
    cout << "\n=== START DEMONSTRATION MODE ===\n";
    this_thread::sleep_for(chrono::seconds(1));

    cout << "\n\n--- ADD 5 ELEMENTS TO DATABASE ---\n\n";
    this_thread::sleep_for(chrono::seconds(1));
    for (int i = 0; i < 5; i++)
    {
        addElement(bufferDatabase, true, false);
    }
    cout << "\n=== Elements added succesfully! ===\n";
    this_thread::sleep_for(chrono::seconds(1));

    cout << "\n\n--- SAVE THE DATABASE ---\n\n";
    this_thread::sleep_for(chrono::seconds(1));
    demonstrationDatabase = bufferDatabase;
    cout << "\n=== Database saved successfully! ===\n";
    this_thread::sleep_for(chrono::seconds(1));

    cout << "\n\n--- RECORD THE DATABASE ---\n\n";
    this_thread::sleep_for(chrono::seconds(1));
    bufferDatabase = demonstrationDatabase;
    cout << "\n=== Database was recorded successfully! ===\n";
    this_thread::sleep_for(chrono::seconds(1));

    cout << "\n\n--- PRINT THE DATABASE ---\n\n";
    this_thread::sleep_for(chrono::seconds(1));
    readAllDatabase(bufferDatabase);
    cout << "\n=== Database was read successfully! ===\n";
    this_thread::sleep_for(chrono::seconds(1));

    cout << "\n\n--- SEARCH THE DATABASE FOR ALL ELEMENTS STARTING WITH THE LETTER 'A' AND HAVING A NUMBER FROM 0 TO 100 -- - \n\n";
    this_thread::sleep_for(chrono::seconds(1));
    vector<Product> name = search(bufferDatabase, true, "a", true, 0, 100, false, zeroValueDate);

    if (name.empty() != 0)
        cout << "\n### Elements not founded! ###\n";
    else
    {
        cout << "\nAll founded elements: \n";
        this_thread::sleep_for(chrono::seconds(1));
        for (auto& p : name)
            p.printInfo();
    }
    this_thread::sleep_for(chrono::seconds(1));

    cout << "\n\n--- CHANGE ELEMENT WITH 1 ID IN DATABASE. CHANGE THE ELEMENT NAME TO 'MILK' --- \n\n";
    this_thread::sleep_for(chrono::seconds(1));
    bufferDatabase[0].name = "Milk";
    cout << "\n=== Name changed succesfully! === \n";
    this_thread::sleep_for(chrono::seconds(1));

    cout << "\n\n--- DELETE ELEMENT WITH ID 5 IN THE DATABASE ---\n\n";
    this_thread::sleep_for(chrono::seconds(1));
    bufferDatabase.erase(bufferDatabase.begin() + 4);
    cout << "\n=== Element with ID 5 was deleted! ===\n";

    cout << "\n\n--- SAVE THE DATABASE ---\n\n";
    this_thread::sleep_for(chrono::seconds(1));
    demonstrationDatabase = bufferDatabase;
    cout << "\n=== Database was saved successfully! ===\n";
    this_thread::sleep_for(chrono::seconds(1));

    cout << "\n\n--- PRINT THE DATABASE ---\n\n";
    this_thread::sleep_for(chrono::seconds(1));
    readAllDatabase(bufferDatabase);
    this_thread::sleep_for(chrono::seconds(1));
    cout << "\n=== Database was read successfully! ===\n";
    this_thread::sleep_for(chrono::seconds(1));

    cout << "\n\n--- EXIT ---\n\n";
    this_thread::sleep_for(chrono::seconds(1));
    cout << "\n=== DATABASE CLOSE ===";
}
void benchmarkMode()
{
    cout << "\n=== Benchmark mode ===\n";

    string txt = "benchmarkTxt.txt", bin = "benchmarkBin.bin";
    fstream benchmarkTxt(txt, ios::app), benchmarkBin(bin, ios::app | ios::binary);
    vector<Product> benchmarkVector, searching;
    date zeroValueDate(0, 0, 0, 0, 0, 0);

    int num;
    do { num = getValidInput<int>("Enter a number of element for database: "); } while (num < 1);

    for (int mode = 2; mode >= 0; mode--)
    {
        vector<Product> buffer;
        buffer.reserve(num);
        string file = txt;
        bool isTxtDatabse = true;
        if (mode == 2)
            cout << "\n=== START BENCHMARK TXT DATABASE ===\n";
        else if (mode == 1)
        {
            cout << "\n\n=== START BENCHMARK BIN DATABASE ===\n";
            file = bin;
            isTxtDatabse = false;
        }
        else
        {
            cout << "\n\n=== START BENCHMARK VECTORE DATABASE ===\n";
            buffer.clear();
        }
        auto startTime = chrono::high_resolution_clock::now();
        auto startTimeAdd = chrono::high_resolution_clock::now();
        for (int i = 0; i < num; i++)
            addElement(buffer, generateRandomElem, benchmark);

        auto endTimeAdd = chrono::high_resolution_clock::now();

        auto startTimeRecord = chrono::high_resolution_clock::now();
        if (mode != 0) recordDatabase(file, buffer, isTxtDatabse, benchmark);
        else benchmarkVector = buffer;
        auto endTimeRecord = chrono::high_resolution_clock::now();

        auto startTimeRestore = chrono::high_resolution_clock::now();
        if (mode != 0) restore(file, buffer, isTxtDatabse, benchmark);
        else buffer = benchmarkVector;
        auto endTimeRestore = chrono::high_resolution_clock::now();

        auto startTimeSearchAll = chrono::high_resolution_clock::now();

        auto startTimeSearchName = chrono::high_resolution_clock::now();
        vector<Product> searching = search(buffer, findName, generateString(rand() % 3 + 1), !findNumOfUnit, ZeroValue, ZeroValue, !findDate, zeroValueDate);
        auto endTimeSearchName = chrono::high_resolution_clock::now();

        double startDiap = static_cast<double>(rand() % 1000) / 10.0;
        double endDiap = static_cast<double>(rand() % 1000) / 10.0;
        if (startDiap > endDiap) swap(startDiap, endDiap);

        auto startTimeSearchQuantity = chrono::high_resolution_clock::now();
        searching = search(buffer, !findName, "", findNumOfUnit, startDiap, endDiap, !findDate, zeroValueDate);
        auto endTimeSearchQuantity = chrono::high_resolution_clock::now();

        auto startTimeSearchDate = chrono::high_resolution_clock::now();
        searching = search(buffer, !findName, "", !findNumOfUnit, ZeroValue, ZeroValue, findDate, getRandomDate());
        auto endTimeSearchDate = chrono::high_resolution_clock::now();
        auto endTimeSearchAll = chrono::high_resolution_clock::now();
        auto endTime = chrono::high_resolution_clock::now();

        auto duration = chrono::duration_cast<chrono::milliseconds>(endTime - startTime);
        auto durationAdd = chrono::duration_cast<chrono::milliseconds>(endTimeAdd - startTimeAdd);
        auto durationRecord = chrono::duration_cast<chrono::milliseconds>(endTimeRecord - startTimeRecord);
        auto durationSearchName = chrono::duration_cast<chrono::milliseconds>(endTimeSearchName - startTimeSearchName);
        auto durationSearchQuantity = chrono::duration_cast<chrono::milliseconds>(endTimeSearchQuantity - startTimeSearchQuantity);
        auto durationSearchDate = chrono::duration_cast<chrono::milliseconds>(endTimeSearchDate - startTimeSearchDate);
        auto durationSearchAll = chrono::duration_cast<chrono::milliseconds>(endTimeSearchAll - startTimeSearchAll);

        auto durationRestore = chrono::duration_cast<chrono::milliseconds>(endTimeRestore - startTimeRestore);
        cout << "\n=============================\n";
        cout << "\nTime add: " << durationAdd.count() << " milliseconds\n";;
        cout << "\nRecording time: " << durationRecord.count() << " milliseconds\n";;
        cout << "\nRestore time: " << durationRestore.count() << " milliseconds\n";;
        cout << "\nSearch time by name: " << durationSearchName.count() << " milliseconds\n";;
        cout << "\nSearch time by quantity: " << durationSearchDate.count() << " milliseconds\n";;
        cout << "\nSearch time by date: " << durationSearchDate.count() << " milliseconds\n";;
        cout << "\nTotal search time: " << durationSearchAll.count() << " milliseconds\n";;
        cout << "\nTotal working time: " << duration.count() / 1000.0 << "seconds\n";
        if (mode == 0) cout << "\nSize: " << sizeof(buffer[0]) * num / 1024.0 / 1024.0 << " Mb \n";
        cout << "\n=============================\n";

    }
    benchmarkBin.close();
    benchmarkTxt.close();


    cout << "\n\n=== BENCHMARK OVER ===\n";

}

void addElement(vector<Product>& bufferDatabase, bool randomElement, bool isBenchmark)
{
    Product newProduct;
    if (!randomElement) newProduct.getInfo();
    else newProduct = generateRandomElement();
    bufferDatabase.empty() ? newProduct.id = 1 : newProduct.id = bufferDatabase[bufferDatabase.size() - 1].id + 1;
    bufferDatabase.push_back(newProduct);
    if (!isBenchmark) cout << "\n=== Product added to database buffer successfully! ===\n";
}
void recordDatabase(const string& filename, const vector<Product>& bufferDatabase, bool isTxtDatabase, bool isBenchmark)
{
    ofstream clearFile(filename, ios::trunc);
    clearFile.close();
    ios_base::openmode fileMode = isTxtDatabase ? ios::in : ios::in | ios::binary;
    ofstream outputFile(filename, fileMode);

    if (!outputFile.is_open())
    {
        cerr << "\n### Error opening the file '" << filename << "'! ###\n";
        return;
    }

    for (const Product& product : bufferDatabase)
    {
        outputFile << product.id << ' ' << product.name << ' ' << product.unit << ' ' << product.quantity << ' ';
        outputFile << product.production_date.year << ' ' << product.production_date.month << ' ' << product.production_date.day << ' ';
        outputFile << product.production_date.hour << ' ' << product.production_date.minute << ' ' << product.production_date.second << ' ';
        outputFile << product.shelf_life << '\n';
    }

    if (!isBenchmark) cout << "\n=== Database has been recorded to the file '" << filename << "'! ===\n";
    outputFile.close();
}
void readAllDatabase(vector<Product>& readVector)
{
    readVector.empty() == 0 ? cout << "\nAll element in databse: \n" : cout << "\n### Database buffer is clear! ###\n";
    for (auto& p : readVector)
      p.printInfo();
}
void restore(const string& filename, vector<Product>& bufferDatabase, bool isTxtDatabase, bool isBenchmark)
{
    ios_base::openmode fileMode = isTxtDatabase ? ios::out : ios::out | ios::binary ;
    ifstream readFile(filename, fileMode);
    bufferDatabase.clear();

    if (!readFile.is_open()) {
        cerr << "\n### Error opening the file '" << filename << "'! ###\n";
        return;
    }

    Product product;
    while (readFile >> product.id >> product.name >> product.unit >> product.quantity
        >> product.production_date.year >> product.production_date.month >> product.production_date.day
        >> product.production_date.hour >> product.production_date.minute >> product.production_date.second
        >> product.shelf_life)
    {

        bufferDatabase.push_back(product);
    }

    if (!isBenchmark) cout << "\n=== Database has been restored/copy from the file '" << filename << "' to database buffer. ===\n";
    readFile.close();
}
void searchElementsManage(vector<Product>& bufferDatabase) {
    vector<Product> allCoincidence;
    string fragment;
    double diaposoneStart = 0, diaposoneEnd = 0;
    date startDate = { 0 };
    bool name = false, numOfUnit = false, checkDate = false;
    int criterion;
    do {
        criterion = getValidInput<int>("Select criterion:\n1. Product name\n2. Quantity of products: \n3. Date of manufacture of the product\n0. Exit\nPlease, enter a number of criterion:");
        switch (criterion) {
        case 0:
            break;
        case 1:
            fragment = getValidInput<string>("Enter a product name: ");
            name = true;
            break;
        case 2:
            cout << "\n=== Enter the range of the number of products ===\n";
            do { diaposoneStart = getValidInput<double>("Enter the smallest value: "); } while (diaposoneStart < 0);
            do { diaposoneEnd = getValidInput<double>("Enter the greatest value: "); } while (diaposoneStart < 0);
            numOfUnit = true;
            break;
        case 3:
            cout << "Enter start date (YYYY MM DD HH MM SS): ";
            startDate.getDate();
            checkDate = true;
            break;
        default:
            cerr << "\n### You entered a wrong number! ###\n";
            break;
        }
    } while (criterion != 0);

    if (!name && !numOfUnit && !checkDate) {
        cout << "\n### You didn't select any criterion! ###\n";
        return;
    }

    allCoincidence = search(bufferDatabase, name, fragment, numOfUnit, diaposoneStart, diaposoneEnd, checkDate, startDate);

    if (allCoincidence.empty()) cout << "\n### Products didn`t founded! ###\n";
    else 
    {
        cout << "\nFounded products: \n";
        for(auto & p : allCoincidence) { p.printInfo(); }
    }
}
vector<Product> search(vector<Product> bufferDatabase, bool name, string fragment, bool numOfUnit, double diaposoneStart, double diaposoneEnd, bool checkDate, date startDate)
{
    vector<Product> allCoincidence;
    for (int i = 0; i < bufferDatabase.size(); i++)
    {
        if ((name && bufferDatabase[i].name.find(fragment) != 0) ||
            (numOfUnit && (bufferDatabase[i].quantity > diaposoneEnd ||
                bufferDatabase[i].quantity < diaposoneStart)) || (checkDate && startDate > bufferDatabase[i].production_date))
            continue;
        allCoincidence.push_back(bufferDatabase[i]);
    }
    return allCoincidence;
}
void modifyElement(vector<Product>& bufferDatabase)
{
    int idModify;
    idModify = getValidInput<int>("\nEnter the ID of the item you want to change: ");
    for (int i = 0; i < bufferDatabase.size(); i++)
    {
        if (bufferDatabase[i].id == idModify)
        {
            cout << "\n=== Product founded! ===\n";
            int operation;
            bool changed = false;
            do
            {
                changed ? cout << "\nDo you want to change anything else?\n" : cout << "\nWhat do you want to change?\n";
                operation = getValidInput<int>("1. Product name\n2. Product unit\n3. Quantity of products\n4. Product production date\n5. Product shelf life\n0. Nothing\nEnter opetarion: ");
                changed = true;

                switch (operation)
                {
                case 0:
                    break;
                case 1:
                    bufferDatabase[i].name = getValidInput<string>("Enter a new name: ");
                    cout << "\n=== Name changed succesfully! ===\n";
                    break;
                case 2:
                    bufferDatabase[i].unit = getValidInput<string>("Enter a new unit: ");
                    cout << "\n=== Unit changed succesfully! ===\n";
                    break;
                case 3:
                    do { bufferDatabase[i].quantity = getValidInput<double>("Enter a new quantity: "); } while (bufferDatabase[i].quantity < 0);
                    cout << "\n=== Quantity changed succesfully! ===\n";
                    break;
                case 4:
                    cout << "Enter a new production date: ";
                    bufferDatabase[i].production_date.getDate();
                    cout << "\n=== Production date changed succesfully! ===\n";
                    break;
                case 5:
                    do { bufferDatabase[i].shelf_life = getValidInput<int>("Enter a new shelf life(in days. Days must be less than 3660): "); } while (bufferDatabase[i].shelf_life < 0 || bufferDatabase[i].shelf_life > 3660);
                    cout << "\n=== Shelf life changed succesfully! ===\n";
                    break;
                default:
                    cout << "\n### You enter wrong number! ###\n";
                    break;
                }
            } while (operation != 0);
            break;
        }
    }
}
void delElement(vector<Product>& bufferDatabase)
{
    int operation;
    operation = getValidInput<int>("\nSelect operation for delete:\n1. Delete element in database buffer\n2. Delete all database buffer\n0. Exit\nEnter operation: ");
    if (operation <= 0 || operation > 2) return;

    if (operation == 1)
    {
        int delId;
        delId = getValidInput<int>("Enter the ID of the product you want to share: ");
        bool deleted;
        Product product;
        for (int i = 0; i < bufferDatabase.size(); i++)
        {
            if (bufferDatabase[i].id == delId)
            {
                deleted = true;
                bufferDatabase.erase(bufferDatabase.begin() + i);
            }
        }

        if (deleted) cout << "\n=== Product with id " << delId << " deleted! ===\n";
        else  cout << "\n### Element with id " << delId << " didn`t deleted! ###\n";

        return;
    }
    else
    {
        bufferDatabase.clear();
        cout << "\n=== Database buffer deleted succesfully! ===\n";
    }
}

Product generateRandomElement()
{
    Product randomElement;
    string units[] = { "kg", "piece", "package", "liter" };
    randomElement.name = generateString(rand() % 15 + 1);
    randomElement.unit = units[rand() % 4];
    randomElement.quantity = (randomElement.unit == "liter" || randomElement.unit == "kg") ? static_cast<double>(rand() % 1000) / 10.0 : rand() % 100;
    randomElement.production_date = getRandomDate();
    randomElement.shelf_life = rand() % 3360;

    return randomElement;
}
string generateString(int len)
{
    string randomString;
    for (int i = 0; i < len; i++)
        randomString += char(97 + rand() % 26);

    return randomString;
}
date getRandomDate()
{
    date randomDate;
    randomDate.year = rand() % 10 + 2015;
    randomDate.month = rand() % 12 + 1;
    randomDate.day = rand() % randomDate.dayInMonth(randomDate.month) + 1;
    randomDate.hour = rand() % 60;
    randomDate.minute = rand() % 60;
    randomDate.second = rand() % 60;
    return randomDate;
}
