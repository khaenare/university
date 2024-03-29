#include <iostream>
#include <string>
#include <vector>
#include <list>
#include <chrono>
#include <sstream>
using namespace std;
using namespace std::chrono;
const int MAX_SIZE = 15000;
const int NUM_ITERATIONS = 15000; // Кількість ітерацій для кожного тесту



bool isValidIP(const string& IP);
void printMenu();
void Append(int structureChoice, string fixedList[], int& fixedListSize, vector<string>& dynamicList, list<string>& linkedList, string IP);
void Insert(int structureChoice, string fixedList[], int& fixedListSize, vector<string>& dynamicList, list<string>& linkedList, string IP, int index);
void Remove(int structureChoice, string fixedList[], int& fixedListSize, vector<string>& dynamicList, list<string>& linkedList, int index);
void Get(int structureChoice, string fixedList[], int fixedListSize, vector<string>& dynamicList, list<string>& linkedList, int index);
void Set(int structureChoice, string fixedList[], int fixedListSize, vector<string>& dynamicList, list<string>& linkedList, string IP, int index);
void Length(int structureChoice, int fixedListSize, vector<string>& dynamicList, list<string>& linkedList);


void basicMode();
void benchmarkMode();
void demonstrationMode();


int main() {

    int mode;
    cout << "Select mode:\n1. Basic Mode\n2. Demonstration mode \n3. Benchmark mode:\nEnter a number of mode: ";
    cin >> mode;

    switch (mode) {
        case 1:
            basicMode();
            break;
        case 2:
            demonstrationMode();
            break;
        case 3:
            benchmarkMode();
            break;
        default:
            cerr << "Error! You enter incorrect mode\n";
            break;
    }
    return 0;
}


void basicMode(){

    string fixedList[MAX_SIZE];
    int fixedListSize = 0;
    vector<string> dynamicList;
    list<string> linkedList;

    int structureChoice, choice, index;
    string IP;
    bool k;
    cout << "Select structure:\n1. Fixed-size array\n2. Dynamic array\n3. Double linked list\nYour choice: ";
    cin >> structureChoice;

    do {
        printMenu();
        cin >> choice;

        switch (choice) {
            case 1:
                cout << "Enter IPv4 to append: ";
                do{
                    cin >> IP;
                    k = isValidIP(IP);
                    if(!k) cout << "Invalid IPv4 input. Please try again.\n";
                } while (!k);
                Append(structureChoice, fixedList, fixedListSize, dynamicList, linkedList, IP);
                break;
            case 2:
                cout << "Enter index and IPv4 to insert: ";
                cin >> index;
                do{
                    cin >> IP;
                    k = isValidIP(IP);
                    if(!k) cout << "Invalid IPv4 input. Please try again.\n";
                } while (!k);
                Insert(structureChoice, fixedList, fixedListSize, dynamicList, linkedList, IP, index);
                break;
            case 3:
                cout << "Enter index to remove: ";
                cin >> index;
                Remove(structureChoice, fixedList, fixedListSize, dynamicList, linkedList, index);
                break;
            case 4:
                cout << "Enter index to get IPv4: ";
                cin >> index;
                Get(structureChoice, fixedList, fixedListSize, dynamicList, linkedList, index);
                break;
            case 5:
                cout << "Enter index and new IPv4 to set: ";
                cin >> index;
                do{
                    cin >> IP;
                    k = isValidIP(IP);
                    if(!k) cout << "Invalid IPv4 input. Please try again.\n";
                } while (!k);
                Set(structureChoice, fixedList, fixedListSize, dynamicList, linkedList, IP, index);
                break;
            case 6:
                Length(structureChoice, fixedListSize, dynamicList, linkedList);
                break;
            case 7:
                cout << "Exiting program.\n";
                break;
            default:
                cout << "Invalid choice. Please try again.\n";
                break;
        }
    } while (choice != 7);
}

void benchmarkMode() {
    cout << "Benchmark mode started.\n\n";

    string fixedList[MAX_SIZE];
    int fixedListSize = 0;
    vector<string> dynamicList;
    list<string> linkedList;


    // Бенчмарк для Append
    auto start = high_resolution_clock::now();
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        Append(1, fixedList, fixedListSize, dynamicList, linkedList, "192.168.1.0");
    }
    auto stop = high_resolution_clock::now();
    auto duration = duration_cast<microseconds>(stop - start);
    cout << "Append (Fixed-size array): " << duration.count() << " microseconds\n";

    start = high_resolution_clock::now();
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        Append(2, fixedList, fixedListSize, dynamicList, linkedList, "192.168.1.0");
    }
    stop = high_resolution_clock::now();
    duration = duration_cast<microseconds>(stop - start);
    cout << "Append (Dynamic array): " << duration.count() << " microseconds\n";

    start = high_resolution_clock::now();
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        Append(3, fixedList, fixedListSize, dynamicList, linkedList, "192.168.1.0");
    }
    stop = high_resolution_clock::now();
    duration = duration_cast<microseconds>(stop - start);
    cout << "Append (Double linked list): " << duration.count() << " microseconds\n\n";


    // Бенчмарк для Insert
    start = high_resolution_clock::now();
    for (int i = 0; i < min(NUM_ITERATIONS, MAX_SIZE)/3; i=i+2) {
        Insert(1, fixedList, fixedListSize, dynamicList, linkedList, "192.168.2.0", i / 2);
    }
    stop = high_resolution_clock::now();
    duration = duration_cast<microseconds>(stop - start);
    cout << "Insert (Fixed-size array): " << duration.count()*6 << " microseconds\n";

    start = high_resolution_clock::now();
    for (int i = 0; i < min(NUM_ITERATIONS, MAX_SIZE)/3; i=i+2) {
        Insert(2, fixedList, fixedListSize, dynamicList, linkedList, "192.168.2.0", i / 2);
    }
    stop = high_resolution_clock::now();
    duration = duration_cast<microseconds>(stop - start);
    cout << "Insert (Dynamic array): " << duration.count()*6 << " microseconds\n";

    start = high_resolution_clock::now();
    for (int i = 0; i < min(NUM_ITERATIONS, MAX_SIZE)/3; i=i+2) {
        Insert(3, fixedList, fixedListSize, dynamicList, linkedList, "192.168.2.0", i / 2);
    }
    stop = high_resolution_clock::now();
    duration = duration_cast<microseconds>(stop - start);
    cout << "Insert (Double linked list): " << duration.count()*6 << " microseconds\n\n";


    // Бенчмарк для Set
    start = high_resolution_clock::now();
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        Set(1, fixedList, fixedListSize, dynamicList, linkedList, "192.168.2.0", i);
    }
    stop = high_resolution_clock::now();
    duration = duration_cast<microseconds>(stop - start);
    cout << "Set (Fixed-size array): " << duration.count() << " microseconds\n";

    start = high_resolution_clock::now();
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        Set(2, fixedList, fixedListSize, dynamicList, linkedList, "192.168.2.0", i);
    }
    stop = high_resolution_clock::now();
    duration = duration_cast<microseconds>(stop - start);
    cout << "Set (Dynamic array): " << duration.count() << " microseconds\n";

    start = high_resolution_clock::now();
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        Set(3, fixedList, fixedListSize, dynamicList, linkedList, "192.168.2.0", i);
    }
    stop = high_resolution_clock::now();
    duration = duration_cast<microseconds>(stop - start);
    cout << "Set (Double linked list): " << duration.count() << " microseconds\n\n";


    // Бенчмарк для Remove
    start = high_resolution_clock::now();
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        Remove(1, fixedList, fixedListSize, dynamicList, linkedList, i);
    }
    stop = high_resolution_clock::now();
    duration = duration_cast<microseconds>(stop - start);
    cout << "Remove (Fixed-size array): " << duration.count() << " microseconds\n";

    start = high_resolution_clock::now();
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        Remove(2, fixedList, fixedListSize, dynamicList, linkedList, i);
    }
    stop = high_resolution_clock::now();
    duration = duration_cast<microseconds>(stop - start);
    cout << "Remove (Dynamic array): " << duration.count() << " microseconds\n";

    start = high_resolution_clock::now();
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        Remove(3, fixedList, fixedListSize, dynamicList, linkedList, i);
    }
    stop = high_resolution_clock::now();
    duration = duration_cast<microseconds>(stop - start);
    cout << "Remove (Double linked list): " << duration.count() << " microseconds\n";
}

void demonstrationMode() {

    cout << "Demonstration mode:\n\n";

    string fixedList[MAX_SIZE];
    int fixedListSize = 0;
    vector<string> dynamicList;
    list<string> linkedList;

    cout << "Fixed-size array operations:\n";
    Append(1, fixedList, fixedListSize, dynamicList, linkedList, "192.168.0.3");
    cout << "\nAppend: "; Get(1, fixedList, fixedListSize, dynamicList, linkedList, 0);
    Insert(1, fixedList, fixedListSize, dynamicList, linkedList, "192.168.1.3", 0);
    cout << "\nInsert to 0: "; Get(1, fixedList, fixedListSize, dynamicList, linkedList, 0);
    Remove(1, fixedList, fixedListSize, dynamicList, linkedList, 0);
    cout << "\nRemove 0: "; Get(1, fixedList, fixedListSize, dynamicList, linkedList, 0);
    Set(1, fixedList, fixedListSize, dynamicList, linkedList, "192.168.2.4", 0);
    cout << "\nSet 0: "; Get(1, fixedList, fixedListSize, dynamicList, linkedList, 0);
    Length(1, fixedListSize, dynamicList, linkedList);
    cout << endl;

    cout << "\nDynamic array operations:\n";
    Append(2, fixedList, fixedListSize, dynamicList, linkedList, "192.168.0.3");
    cout << "\nAppend: "; Get(2, fixedList, fixedListSize, dynamicList, linkedList, 0);
    Insert(2, fixedList, fixedListSize, dynamicList, linkedList, "192.168.1.3", 0);
    cout << "\nInsert to 0: "; Get(2, fixedList, fixedListSize, dynamicList, linkedList, 0);
    Remove(2, fixedList, fixedListSize, dynamicList, linkedList, 0);
    cout << "\nRemove 0: "; Get(2, fixedList, fixedListSize, dynamicList, linkedList, 0);
    Set(2, fixedList, fixedListSize, dynamicList, linkedList, "192.168.2.4", 0);
    cout << "\nSet 0: "; Get(2, fixedList, fixedListSize, dynamicList, linkedList, 0);
    Length(2, fixedListSize, dynamicList, linkedList);
    cout << endl;

    cout << "\nLinked list operations:\n";
    Append(3, fixedList, fixedListSize, dynamicList, linkedList, "192.168.0.3");
    cout << "\nAppend: "; Get(3, fixedList, fixedListSize, dynamicList, linkedList, 0);
    Insert(3, fixedList, fixedListSize, dynamicList, linkedList, "192.168.1.3", 0);
    cout << "\nInsert to 0: "; Get(3, fixedList, fixedListSize, dynamicList, linkedList, 0);
    Remove(3, fixedList, fixedListSize, dynamicList, linkedList, 0);
    cout << "\nRemove o: "; Get(3, fixedList, fixedListSize, dynamicList, linkedList, 0);
    Set(3, fixedList, fixedListSize, dynamicList, linkedList, "192.168.2.4", 0);
    cout << "\nSet o: "; Get(3, fixedList, fixedListSize, dynamicList, linkedList, 0);
    Length(3, fixedListSize, dynamicList, linkedList);
    cout << endl;
}





bool isValidIP(const string& IP) {
    stringstream ss(IP);
    string segment;
    int num, segmentCount = 0;

    while (getline(ss, segment, '.')) {
        if (++segmentCount > 4) return false; // Більше ніж 4 сегменти
        if (!(stringstream(segment) >> num)) return false; // Не числове значення
        if (num <= 0 || num >= 255) return false; // Не в діапазоні [0, 255]
    }
    return segmentCount == 4; // Повинно бути рівно 4 сегменти
}

void printMenu() {
    cout << "\nChoose operation:\n"
         << "1. Append\n"
         << "2. Insert\n"
         << "3. Remove\n"
         << "4. Get\n"
         << "5. Set\n"
         << "6. Length\n"
         << "7. Exit\n"
         << "Your choice: ";
}

void Append(int structureChoice, string fixedList[], int& fixedListSize, vector<string>& dynamicList, list<string>& linkedList, string IP){
    if (structureChoice == 1) {
        if (fixedListSize >= MAX_SIZE) {
            cerr << "Error: Fixed-size array is full." << endl;
        } else {
            fixedList[fixedListSize++] = IP;
        }
    } else if (structureChoice == 2) {
        dynamicList.push_back(IP);
    } else if (structureChoice == 3) {
        linkedList.push_back(IP);
    }

}

void Insert(int structureChoice, string fixedList[], int& fixedListSize, vector<string>& dynamicList, list<string>& linkedList, string IP, int index){
    if (structureChoice == 1 && index >= 0 && index < fixedListSize) {
        if (fixedListSize >= MAX_SIZE) {
            cerr << "Error: Fixed-size array is full." << endl;
        } else {
            for (int i = fixedListSize; i > index; --i) fixedList[i] = fixedList[i - 1];
            fixedList[index] = IP;
            fixedListSize++;
        }
    } else if (structureChoice == 2 && index >= 0 && index <= dynamicList.size()) {
        dynamicList.insert(dynamicList.begin() + index, IP);
    } else if (structureChoice == 3 && index >= 0 && index <= linkedList.size()) {
        auto it = linkedList.begin();
        advance(it, index);
        linkedList.insert(it, IP);
    }
}

void Remove(int structureChoice, string fixedList[], int& fixedListSize, vector<string>& dynamicList, list<string>& linkedList, int index){
    if (structureChoice == 1 && index >= 0 && index < fixedListSize) {
        for (int i = index; i < fixedListSize - 1; ++i) fixedList[i] = fixedList[i + 1];
        fixedListSize--;
    } else if (structureChoice == 2 && index >= 0 && index < dynamicList.size()) {
        dynamicList.erase(dynamicList.begin() + index);
    } else if (structureChoice == 3 && index >= 0 && index < linkedList.size()) {
        auto it = linkedList.begin();
        advance(it, index);
        linkedList.erase(it);
    }
}

void Get(int structureChoice, string fixedList[], int fixedListSize, vector<string>& dynamicList, list<string>& linkedList, int index){
    if (structureChoice == 1 && index >= 0 && index < fixedListSize) {
        cout << "IP: " << fixedList[index] << endl;
    } else if (structureChoice == 2 && index >= 0 && index < dynamicList.size()) {
        cout << "IP: " << dynamicList[index] << endl;
    } else if (structureChoice == 3 && index >= 0 && index < linkedList.size()) {
        auto hehe = linkedList.begin();
        advance(hehe, index);
        cout << "IP: " << *hehe << endl;
    }
}

void Set(int structureChoice, string fixedList[], int fixedListSize, vector<string>& dynamicList, list<string>& linkedList, string IP, int index){
    if (structureChoice == 1) {
        if (index >= 0 && index < fixedListSize) {
            fixedList[index] = IP;
        } else {
            cerr << "Error: Index out of borders of fixed-size array.\n";
        }
    } else if (structureChoice == 2) {
        if (index >= 0 && index < dynamicList.size()) {
            dynamicList[index] = IP;
        } else {
            cerr << "Error: Index out of borders of dynamic array.\n";
        }
    } else if (structureChoice == 3) {
        if (index >= 0 && index < linkedList.size()) {
            auto meme = linkedList.begin();
            advance(meme, index);
            *meme = IP;
        } else {
            cerr << "Error: Index out of borders of double linked list.\n";
        }
    }
}

void Length(int structureChoice, int fixedListSize, vector<string>& dynamicList, list<string>& linkedList){
    if (structureChoice == 1) {
        cout << "Length: " << fixedListSize << endl;
    } else if (structureChoice == 2) {
        cout << "Length: " << dynamicList.size() << endl;
    } else if (structureChoice == 3) {
        cout << "Length: " << linkedList.size() << endl;
    }
}
