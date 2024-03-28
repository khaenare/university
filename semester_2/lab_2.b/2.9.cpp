#include <iostream>
#include <string>
#include <chrono>
using namespace std;
using namespace std::chrono;

struct Node {
    string value;
    Node* next;
    Node(string value, Node* next = nullptr) : value(value), next(next) {}
};
struct LinkedList {
    Node* start;
    Node* end;
    LinkedList() : start(nullptr), end(nullptr) {}

    ~LinkedList() {
        while (start) {
            Node* temp = start;
            start = start->next;
            delete temp;
        }
    }

    void append(string value) {
        Node* newNode = new Node(value);
        if (end) {
            end->next = newNode;
        } else {
            start = newNode;
        }
        end = newNode;
    }
    void print() const {
        Node* current = start;
        while (current) {
            cout << current->value << ", ";
            current = current->next;
        }
        cout << endl;
    }
};
LinkedList zip(const LinkedList& list1, const LinkedList& list2, const string& strategy, const string& fixedValue = "") {
    LinkedList result;
    Node* current1 = list1.start;
    Node* current2 = list2.start;

    while (current1 || current2) {
        if (current1) {
            result.append(current1->value);
            current1 = current1->next;
        } else if (strategy == "TakeBoth" || strategy == "UseFixedValue") {
            result.append(fixedValue);
        }

        if (current2) {
            result.append(current2->value);
            current2 = current2->next;
        } else if (strategy == "TakeBoth" || strategy == "UseFixedValue") {
            result.append(fixedValue);
        }

        if (strategy == "DropExtra" && (!current1 || !current2)) {
            break;
        }
    }
    return result;
}

void printPairs(const LinkedList& list);
void fillList(LinkedList& list);
void basicMode();
void demonstrationMode();
void benchmarkMode();

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

void basicMode() {
    LinkedList list1, list2;
    cout << "Fill the first list (to exit enter 'exit'): " << endl;
    fillList(list1);
    cout << "List 1: ";
    list1.print();

    cout << "Fill the second list (to exit enter 'exit'): " << endl;
    fillList(list2);
    cout << "List 2: ";
    list2.print();

    string strategy, fixedValue;
    cout << "Enter zip strategy (DropExtra, TakeBoth, UseFixedValue): ";
    cin >> strategy;
    if (strategy == "UseFixedValue") {
        cout << "Enter fixed value: ";
        cin >> fixedValue;
    }

    LinkedList zippedList = zip(list1, list2, strategy, fixedValue);
    cout << "Zipped List: ";
    printPairs(zippedList);
}

void demonstrationMode() {
    LinkedList list1, list2;

    list1.append("1");
    list1.append("2");
    list1.append("3");

    list2.append("A");
    list2.append("B");
    list2.append("C");
    list2.append("D");

    cout << "List 1: ";
    list1.print();
    cout << "List 2: ";
    list2.print();

    cout << "\nDemonstrating 'DropExtra' strategy:\n";
    LinkedList zippedDropExtra = zip(list1, list2, "DropExtra");
    printPairs(zippedDropExtra);

    cout << "\nDemonstrating 'TakeBoth' strategy:\n";
    LinkedList zippedTakeBoth = zip(list1, list2, "TakeBoth");
    printPairs(zippedTakeBoth);

    cout << "\nDemonstrating 'UseFixedValue' strategy with 'X' as fixed value:\n";
    LinkedList zippedUseFixedValue = zip(list1, list2, "UseFixedValue", "X");
    printPairs(zippedUseFixedValue);
}

void benchmarkMode() {
    LinkedList list1, list2;

    for (int i = 0; i < 10000; ++i) {
        list1.append(to_string(i));
        list2.append(to_string(i + 1));
    }

    string strategies[] = {"DropExtra", "TakeBoth", "UseFixedValue"};

    for (const string& strategy : strategies) {
        auto start = high_resolution_clock::now();
        LinkedList zippedList = zip(list1, list2, strategy, "X");
        auto stop = high_resolution_clock::now();
        auto duration = duration_cast<milliseconds>(stop - start);

        cout << "Strategy: " << strategy << ", Time: " << duration.count() << " ms" << endl;
    }
}


void fillList(LinkedList& list) {
    while (true) {
        string el;
        cin >> el;
        if (el == "exit") {
            break;
        } else {
            list.append(el);
        }
    }
}

void printPairs(const LinkedList& list) {
    Node* current = list.start;
    while (current && current->next) {
        cout << "(" << current->value << ", " << current->next->value << ") ";
        current = current->next->next;
    }
    cout << endl;
}
