//Текстові рядки, лексикографічний порядок, за зростанням (“A”<”AA”<”AB”<”B”)

#include <chrono>
#include <iostream>
#include <string>
#include <cstdlib>
#include <ctime>
#include <algorithm>
#include <windows.h>
#include <psapi.h>

using namespace std;
using namespace std::chrono;

// Структура для узла связного списка
struct Node {
    string data;
    Node* next;
};

// Структура для списка на основе массива
const int MAX_SIZE = 100;
struct ArrayList {
    string data[MAX_SIZE];
    int size;
};

// Структура для узла бинарного дерева поиска
struct TreeNode {
    string data;
    TreeNode* left;
    TreeNode* right;
};

// Структура для узла АВЛ-дерева
struct AVLNode {
    string data;
    AVLNode* left;
    AVLNode* right;
    int height;
};

// Структура для узла 2-3 дерева
struct TwoThreeNode {
    string data1, data2;
    TwoThreeNode* child1;
    TwoThreeNode* child2;
    TwoThreeNode* child3;
    int numKeys;
};

// Функции для связного списка
Node* createLinkedList();
void addElement(Node*& head, const string& value);
void removeElement(Node*& head, const string& value);
Node* findElement(Node* head, const string& value);
void findElementsInRange(Node* head, const string& start, const string& end);
void printList(Node* head);
void fillListWithRandomElements(Node*& head, int count);

// Функции для списка на основе массива
ArrayList createArrayList();
void addElement(ArrayList& list, const string& value);
void removeElement(ArrayList& list, const string& value);
int findElement(const ArrayList& list, const string& value);
void findElementsInRange(const ArrayList& list, const string& start, const string& end);
void printList(const ArrayList& list);
void fillListWithRandomElements(ArrayList& list, int count);

// Функции для бинарного дерева поиска
TreeNode* createBinarySearchTree();
TreeNode* addElement(TreeNode* root, const string& value);
TreeNode* removeElement(TreeNode* root, const string& value);
TreeNode* findElement(TreeNode* root, const string& value);
void findElementsInRange(TreeNode* root, const string& start, const string& end);
void printList(TreeNode* root);
void fillTreeWithRandomElements(TreeNode*& root, int count);

// Функции для АВЛ-дерева
AVLNode* createAVLTree();
int getHeight(AVLNode* node);
int getBalance(AVLNode* node);
AVLNode* rotateRight(AVLNode* y);
AVLNode* rotateLeft(AVLNode* x);
AVLNode* addElement(AVLNode* node, const string& value);
AVLNode* minValueNode(AVLNode* node);
AVLNode* removeElement(AVLNode* root, const string& value);
AVLNode* findElement(AVLNode* root, const string& value);
void findElementsInRange(AVLNode* root, const string& start, const string& end);
void printList(AVLNode* root);
void fillTreeWithRandomElements(AVLNode*& root, int count);

// Функции для 2-3 дерева
TwoThreeNode* createTwoThreeTree();
TwoThreeNode* findLeaf(TwoThreeNode* node, const string& value);
TwoThreeNode* splitNode(TwoThreeNode* parent, TwoThreeNode* node, const string& value);
TwoThreeNode* addElement(TwoThreeNode* root, const string& value);
bool findElement(TwoThreeNode* root, const string& value);
void findElementsInRange(TwoThreeNode* root, const string& start, const string& end);
void printList(TwoThreeNode* root);
void fillTreeWithRandomElements(TwoThreeNode*& root, int count);

//херня для бенчмарка
size_t getMemoryUsage() {
    PROCESS_MEMORY_COUNTERS memInfo;
    GetProcessMemoryInfo(GetCurrentProcess(), &memInfo, sizeof(memInfo));
    return memInfo.PeakWorkingSetSize;
}
template<typename Func, typename... Args>
long long measureTime(Func func, Args&&... args) {
    auto start = high_resolution_clock::now();
    func(forward<Args>(args)...);
    auto stop = high_resolution_clock::now();
    auto duration = duration_cast<microseconds>(stop - start);
    return duration.count();
}
void testLinkedList(Node*& head) {
    fillListWithRandomElements(head, 1000);
}
void testArrayList(ArrayList& list) {
    fillListWithRandomElements(list, 1000);
}
void testBST(TreeNode*& root) {
    fillTreeWithRandomElements(root, 1000);
}
void testAVLTree(AVLNode*& root) {
    fillTreeWithRandomElements(root, 1000);
}
void testTwoThreeTree(TwoThreeNode*& root) {
    fillTreeWithRandomElements(root, 1000);
}



void interactiveMode();
void demoMode();
void benchmarkMode();



int main() {
    int mode;
    cout << "Select mode:\n1. Interactive mode \n2. Demonstration mode\n3. Benchmark mode:\nEnter a number of mode: ";
    cin >> mode;

    switch (mode) {
        case 1:
            interactiveMode();
            break;
        case 2:
            demoMode();
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


// Функции для связного списка
Node* createLinkedList() {
    return nullptr;
}

void addElement(Node*& head, const string& value) {
    Node* newNode = new Node{value, nullptr};
    if (!head || head->data > value) {
        newNode->next = head;
        head = newNode;
    } else {
        Node* current = head;
        while (current->next && current->next->data < value) {
            current = current->next;
        }
        newNode->next = current->next;
        current->next = newNode;
    }
}

void removeElement(Node*& head, const string& value) {
    if (!head) return;
    if (head->data == value) {
        Node* temp = head;
        head = head->next;
        delete temp;
    } else {
        Node* current = head;
        while (current->next && current->next->data != value) {
            current = current->next;
        }
        if (current->next) {
            Node* temp = current->next;
            current->next = current->next->next;
            delete temp;
        }
    }
}

Node* findElement(Node* head, const string& value) {
    Node* current = head;
    while (current && current->data != value) {
        current = current->next;
    }
    return current;
}

void findElementsInRange(Node* head, const string& start, const string& end) {
    Node* current = head;
    while (current && current->data < start) {
        current = current->next;
    }
    while (current && current->data <= end) {
        cout << current->data << " ";
        current = current->next;
    }
    cout << endl;
}

void printList(Node* head) {
    Node* current = head;
    while (current) {
        cout << current->data << " ";
        current = current->next;
    }
    cout << endl;
}

void fillListWithRandomElements(Node*& head, int count) {
    srand(time(0));
    for (int i = 0; i < count; ++i) {
        string value = "";
        int len = rand() % 5 + 1;
        for (int j = 0; j < len; ++j) {
            value += 'A' + rand() % 26;
        }
        addElement(head, value);
    }
}

// Функции для списка на основе массива
ArrayList createArrayList() {
    ArrayList list;
    list.size = 0;
    return list;
}

void addElement(ArrayList& list, const string& value) {
    if (list.size < MAX_SIZE) {
        list.data[list.size++] = value;
        sort(list.data, list.data + list.size);
    }
}

void removeElement(ArrayList& list, const string& value) {
    int pos = -1;
    for (int i = 0; i < list.size; ++i) {
        if (list.data[i] == value) {
            pos = i;
            break;
        }
    }
    if (pos != -1) {
        for (int i = pos; i < list.size - 1; ++i) {
            list.data[i] = list.data[i + 1];
        }
        list.size--;
    }
}

int findElement(const ArrayList& list, const string& value) {
    for (int i = 0; i < list.size; ++i) {
        if (list.data[i] == value) {
            return i;
        }
    }
    return -1;
}

void findElementsInRange(const ArrayList& list, const string& start, const string& end) {
    for (int i = 0; i < list.size; ++i) {
        if (list.data[i] >= start && list.data[i] <= end) {
            cout << list.data[i] << " ";
        }
    }
    cout << endl;
}

void printList(const ArrayList& list) {
    for (int i = 0; i < list.size; ++i) {
        cout << list.data[i] << " ";
    }
    cout << endl;
}

void fillListWithRandomElements(ArrayList& list, int count) {
    srand(time(0));
    for (int i = 0; i < count && list.size < MAX_SIZE; ++i) {
        string value = "";
        int len = rand() % 5 + 1;
        for (int j = 0; j < len; ++j) {
            value += 'A' + rand() % 26;
        }
        addElement(list, value);
    }
}

// Функции для бинарного дерева поиска
TreeNode* createBinarySearchTree() {
    return nullptr;
}

TreeNode* addElement(TreeNode* root, const string& value) {
    if (root == nullptr) {
        root = new TreeNode{value, nullptr, nullptr};
    } else if (value < root->data) {
        root->left = addElement(root->left, value);
    } else {
        root->right = addElement(root->right, value);
    }
    return root;
}

TreeNode* removeElement(TreeNode* root, const string& value) {
    if (root == nullptr) return root;
    if (value < root->data) {
        root->left = removeElement(root->left, value);
    } else if (value > root->data) {
        root->right = removeElement(root->right, value);
    } else {
        if (root->left == nullptr) {
            TreeNode* temp = root->right;
            delete root;
            return temp;
        } else if (root->right == nullptr) {
            TreeNode* temp = root->left;
            delete root;
            return temp;
        }
        TreeNode* temp = root->right;
        while (temp && temp->left != nullptr) {
            temp = temp->left;
        }
        root->data = temp->data;
        root->right = removeElement(root->right, temp->data);
    }
    return root;
}

TreeNode* findElement(TreeNode* root, const string& value) {
    if (root == nullptr || root->data == value) {
        return root;
    }
    if (value < root->data) {
        return findElement(root->left, value);
    }
    return findElement(root->right, value);
}

void findElementsInRange(TreeNode* root, const string& start, const string& end) {
    if (root == nullptr) return;
    if (start < root->data) {
        findElementsInRange(root->left, start, end);
    }
    if (start <= root->data && end >= root->data) {
        cout << root->data << " ";
    }
    if (end > root->data) {
        findElementsInRange(root->right, start, end);
    }
}

void printList(TreeNode* root) {
    if (root == nullptr) return;
    printList(root->left);
    cout << root->data << " ";
    printList(root->right);
}

void performAction(TreeNode* root) {
    if (root == nullptr) return;
    performAction(root->left);
    cout << root->data << " ";
    performAction(root->right);
}

void fillTreeWithRandomElements(TreeNode*& root, int count) {
    srand(time(0));
    for (int i = 0; i < count; ++i) {
        string value = "";
        int len = rand() % 5 + 1;
        for (int j = 0; j < len; ++j) {
            value += 'A' + rand() % 26;
        }
        root = addElement(root, value);
    }
}

// Функции для АВЛ-дерева
AVLNode* createAVLTree() {
    return nullptr;
}

int getHeight(AVLNode* node) {
    return node ? node->height : 0;
}

int getBalance(AVLNode* node) {
    return node ? getHeight(node->left) - getHeight(node->right) : 0;
}

AVLNode* rotateRight(AVLNode* y) {
    AVLNode* x = y->left;
    AVLNode* T2 = x->right;
    x->right = y;
    y->left = T2;
    y->height = max(getHeight(y->left), getHeight(y->right)) + 1;
    x->height = max(getHeight(x->left), getHeight(x->right)) + 1;
    return x;
}

AVLNode* rotateLeft(AVLNode* x) {
    AVLNode* y = x->right;
    AVLNode* T2 = y->left;
    y->left = x;
    x->right = T2;
    x->height = max(getHeight(x->left), getHeight(x->right)) + 1;
    y->height = max(getHeight(y->left), getHeight(y->right)) + 1;
    return y;
}

AVLNode* addElement(AVLNode* node, const string& value) {
    if (node == nullptr) {
        return new AVLNode{value, nullptr, nullptr, 1};
    }
    if (value < node->data) {
        node->left = addElement(node->left, value);
    } else if (value > node->data) {
        node->right = addElement(node->right, value);
    } else {
        return node;
    }

    node->height = 1 + max(getHeight(node->left), getHeight(node->right));

    int balance = getBalance(node);

    if (balance > 1 && value < node->left->data) {
        return rotateRight(node);
    }
    if (balance < -1 && value > node->right->data) {
        return rotateLeft(node);
    }
    if (balance > 1 && value > node->left->data) {
        node->left = rotateLeft(node->left);
        return rotateRight(node);
    }
    if (balance < -1 && value < node->right->data) {
        node->right = rotateRight(node->right);
        return rotateLeft(node);
    }

    return node;
}

AVLNode* minValueNode(AVLNode* node) {
    AVLNode* current = node;
    while (current->left != nullptr) {
        current = current->left;
    }
    return current;
}

AVLNode* removeElement(AVLNode* root, const string& value) {
    if (root == nullptr) {
        return root;
    }
    if (value < root->data) {
        root->left = removeElement(root->left, value);
    } else if (value > root->data) {
        root->right = removeElement(root->right, value);
    } else {
        if ((root->left == nullptr) || (root->right == nullptr)) {
            AVLNode* temp = root->left ? root->left : root->right;
            if (temp == nullptr) {
                temp = root;
                root = nullptr;
            } else {
                *root = *temp;
            }
            delete temp;
        } else {
            AVLNode* temp = minValueNode(root->right);
            root->data = temp->data;
            root->right = removeElement(root->right, temp->data);
        }
    }

    if (root == nullptr) {
        return root;
    }

    root->height = 1 + max(getHeight(root->left), getHeight(root->right));

    int balance = getBalance(root);

    if (balance > 1 && getBalance(root->left) >= 0) {
        return rotateRight(root);
    }
    if (balance > 1 && getBalance(root->left) < 0) {
        root->left = rotateLeft(root->left);
        return rotateRight(root);
    }
    if (balance < -1 && getBalance(root->right) <= 0) {
        return rotateLeft(root);
    }
    if (balance < -1 && getBalance(root->right) > 0) {
        root->right = rotateRight(root->right);
        return rotateLeft(root);
    }

    return root;
}

AVLNode* findElement(AVLNode* root, const string& value) {
    if (root == nullptr || root->data == value) {
        return root;
    }
    if (value < root->data) {
        return findElement(root->left, value);
    }
    return findElement(root->right, value);
}

void findElementsInRange(AVLNode* root, const string& start, const string& end) {
    if (root == nullptr) return;
    if (start < root->data) {
        findElementsInRange(root->left, start, end);
    }
    if (start <= root->data && end >= root->data) {
        cout << root->data << " ";
    }
    if (end > root->data) {
        findElementsInRange(root->right, start, end);
    }
}

void printList(AVLNode* root) {
    if (root == nullptr) return;
    printList(root->left);
    cout << root->data << " ";
    printList(root->right);
}

void fillTreeWithRandomElements(AVLNode*& root, int count) {
    srand(time(0));
    for (int i = 0; i < count; ++i) {
        string value = "";
        int len = rand() % 5 + 1;
        for (int j = 0; j < len; ++j) {
            value += 'A' + rand() % 26;
        }
        root = addElement(root, value);
    }
}

// Функции для 2-3 дерева
TwoThreeNode* createTwoThreeTree() {
    return nullptr;
}

TwoThreeNode* findLeaf(TwoThreeNode* node, const string& value) {
    if (!node) return nullptr;
    if (!node->child1) return node;
    if (value < node->data1) return findLeaf(node->child1, value);
    if (node->numKeys == 1 || (node->numKeys == 2 && value < node->data2)) return findLeaf(node->child2, value);
    return findLeaf(node->child3, value);
}

TwoThreeNode* splitNode(TwoThreeNode* parent, TwoThreeNode* node, const string& value) {
    string small, mid, large;
    if (value < node->data1) {
        small = value;
        mid = node->data1;
        large = node->data2;
    } else if (value < node->data2) {
        small = node->data1;
        mid = value;
        large = node->data2;
    } else {
        small = node->data1;
        mid = node->data2;
        large = value;
    }

    TwoThreeNode* newLeft = new TwoThreeNode{small, "", nullptr, nullptr, nullptr, 1};
    TwoThreeNode* newRight = new TwoThreeNode{large, "", nullptr, nullptr, nullptr, 1};

    if (!parent) {
        return new TwoThreeNode{mid, "", newLeft, newRight, nullptr, 1};
    }

    if (parent->numKeys == 1) {
        if (mid < parent->data1) {
            parent->data2 = parent->data1;
            parent->data1 = mid;
            parent->child3 = parent->child2;
            parent->child1 = newLeft;
            parent->child2 = newRight;
        } else {
            parent->data2 = mid;
            parent->child2 = newLeft;
            parent->child3 = newRight;
        }
        parent->numKeys++;
        return parent;
    }

    return splitNode(parent, parent, mid);
}

TwoThreeNode* addElement(TwoThreeNode* root, const string& value) {
    if (!root) {
        return new TwoThreeNode{value, "", nullptr, nullptr, nullptr, 1};
    }

    TwoThreeNode* leaf = findLeaf(root, value);
    if (leaf->numKeys == 1) {
        if (value < leaf->data1) {
            leaf->data2 = leaf->data1;
            leaf->data1 = value;
        } else {
            leaf->data2 = value;
        }
        leaf->numKeys++;
        return root;
    }

    return splitNode(nullptr, leaf, value);
}

bool findElement(TwoThreeNode* root, const string& value) {
    if (!root) return false;
    if (root->data1 == value || (root->numKeys == 2 && root->data2 == value)) return true;
    if (value < root->data1) return findElement(root->child1, value);
    if (root->numKeys == 1 || (root->numKeys == 2 && value < root->data2)) return findElement(root->child2, value);
    return findElement(root->child3, value);
}

void findElementsInRange(TwoThreeNode* root, const string& start, const string& end) {
    if (!root) return;
    if (root->child1 && start < root->data1) findElementsInRange(root->child1, start, end);
    if (start <= root->data1 && end >= root->data1) cout << root->data1 << " ";
    if (root->child2 && ((root->numKeys == 1) || (root->numKeys == 2 && start < root->data2))) findElementsInRange(root->child2, start, end);
    if (root->numKeys == 2 && start <= root->data2 && end >= root->data2) cout << root->data2 << " ";
    if (root->child3 && end > root->data2) findElementsInRange(root->child3, start, end);
}

void printList(TwoThreeNode* root) {
    if (!root) return;
    printList(root->child1);
    cout << root->data1 << " ";
    printList(root->child2);
    if (root->numKeys == 2) {
        cout << root->data2 << " ";
        printList(root->child3);
    }
}

void fillTreeWithRandomElements(TwoThreeNode*& root, int count) {
    srand(time(0));
    for (int i = 0; i < count; ++i) {
        string value = "";
        int len = rand() % 5 + 1;
        for (int j = 0; j < len; ++j) {
            value += 'A' + rand() % 26;
        }
        root = addElement(root, value);
    }
}

void interactiveMode() {
    int structureChoice;
    do {
        cout << "Select the data structure:\n";
        cout << "1. Linked list\n";
        cout << "2. Array-based list\n";
        cout << "3. Binary search tree\n";
        cout << "4. AVL tree\n";
        cout << "5. 2-3 tree\n";
        cout << "0. Exit\n.";
        cout << "Your choice: ";
        cin >> structureChoice;

        if (structureChoice == 0) break;

        int operationChoice;
        Node* linkedList = nullptr;
        ArrayList arrayList = createArrayList();
        TreeNode* bst = createBinarySearchTree();
        AVLNode* avlTree = createAVLTree();
        TwoThreeNode* twoThreeTree = createTwoThreeTree();

        do {
            cout << "Menu of operations:\n";
            cout << "1. Add element\n";
            cout << "2. Delete item\n";
            cout << "3. Find element\n";
            cout << "4. Find elements in the range\n";
            cout << "5. Output the elements\n";
            cout << "6. Fill with random elements\n";
            cout << "0. Go back\n.";
            cout << "Your choice: ";
            cin >> operationChoice;

            string value, start, end;
            int count;

            switch (operationChoice) {
                case 1:
                    cout << "Enter the value to be added: ";
                    cin >> value;
                    if (structureChoice == 1) {
                        addElement(linkedList, value);
                    } else if (structureChoice == 2) {
                        addElement(arrayList, value);
                    } else if (structureChoice == 3) {
                        bst = addElement(bst, value);
                    } else if (structureChoice == 4) {
                        avlTree = addElement(avlTree, value);
                    } else if (structureChoice == 5) {
                        twoThreeTree = addElement(twoThreeTree, value);
                    }
                    break;
                case 2:
                    cout << "Enter the value to be deleted: ";
                    cin >> value;
                    if (structureChoice == 1) {
                        removeElement(linkedList, value);
                    } else if (structureChoice == 2) {
                        removeElement(arrayList, value);
                    } else if (structureChoice == 3) {
                        bst = removeElement(bst, value);
                    } else if (structureChoice == 4) {
                        avlTree = removeElement(avlTree, value);
                    } else if (structureChoice == 5) {
                        cout << "Not implemented :(";
                    }
                    break;
                case 3:
                    cout << "Enter the value to search for: ";
                    cin >> value;
                    if (structureChoice == 1) {
                        if (findElement(linkedList, value)) {
                            cout << "Element found\n";
                        } else {
                            cout << "Element not found\n";
                        }
                    } else if (structureChoice == 2) {
                        if (findElement(arrayList, value) != -1) {
                            cout << "Element found\n";
                        } else {
                            cout << "Element not found\n";
                        }
                    } else if (structureChoice == 3) {
                        if (findElement(bst, value)) {
                            cout << "Element found\n";
                        } else {
                            cout << "Element not found\n";
                        }
                    } else if (structureChoice == 4) {
                        if (findElement(avlTree, value)) {
                            cout << "Element found\n";
                        } else {
                            cout << "Element not found\n";
                        }
                    } else if (structureChoice == 5) {
                        if (findElement(twoThreeTree, value)) {
                            cout << "Element found\n";
                        } else {
                            cout << "Element not found\n";
                        }
                    }
                    break;
                case 4:
                    cout << "Enter the beginning of the range: ";
                    cin >> start;
                    cout << "Enter the end of the range: ";
                    cin >> end;
                    if (structureChoice == 1) {
                        findElementsInRange(linkedList, start, end);
                    } else if (structureChoice == 2) {
                        findElementsInRange(arrayList, start, end);
                    } else if (structureChoice == 3) {
                        findElementsInRange(bst, start, end);
                    } else if (structureChoice == 4) {
                        findElementsInRange(avlTree, start, end);
                    } else if (structureChoice == 5) {
                        findElementsInRange(twoThreeTree, start, end);
                    }
                    break;
                case 5:
                    if (structureChoice == 1) {
                        printList(linkedList);
                    } else if (structureChoice == 2) {
                        printList(arrayList);
                    } else if (structureChoice == 3) {
                        printList(bst);
                    } else if (structureChoice == 4) {
                        printList(avlTree);
                    } else if (structureChoice == 5) {
                        printList(twoThreeTree);
                    }
                    break;
                case 6:
                    cout << "Enter the number of random elements: ";
                    cin >> count;
                    if (structureChoice == 1) {
                        fillListWithRandomElements(linkedList, count);
                    } else if (structureChoice == 2) {
                        fillListWithRandomElements(arrayList, count);
                    } else if (structureChoice == 3) {
                        fillTreeWithRandomElements(bst, count);
                    } else if (structureChoice == 4) {
                        fillTreeWithRandomElements(avlTree, count);
                    } else if (structureChoice == 5) {
                        fillTreeWithRandomElements(twoThreeTree, count);
                    }
                    break;
                case 0:
                    cout << "Go back\n";
                    break;
                default:
                    cout << "Incorrect choice\n";
            }
        } while (operationChoice != 0);
    } while (structureChoice != 0);
}

void demoMode() {
    // Демонстрация для связного списка
    cout << "Demonstration of how a linked list works:\n";
    Node* linkedList = createLinkedList();
    cout << "Adding elements: \n";
    addElement(linkedList, "B");
    addElement(linkedList, "A");
    addElement(linkedList, "AB");
    addElement(linkedList, "AA");
    printList(linkedList);
    cout << "Removal of AA: \n";
    removeElement(linkedList, "AA");
    printList(linkedList);
    cout << "Search from A to B: \n";
    findElementsInRange(linkedList, "A", "B");

    // Демонстрация для списка на основе массива
    cout << "\nDemonstration of array-based list operation:\n";
    ArrayList arrayList = createArrayList();
    cout << "Adding elements: \n";
    addElement(arrayList, "B");
    addElement(arrayList, "A");
    addElement(arrayList, "AB");
    addElement(arrayList, "AA");
    printList(arrayList);
    cout << "Removal of AA: \n";
    removeElement(arrayList, "AA");
    printList(arrayList);
    cout << "Search from A to B: \n";
    findElementsInRange(arrayList, "A", "B");

    // Демонстрация для бинарного дерева поиска
    cout << "\nDemonstration of binary search tree operation:\n";
    TreeNode* bst = createBinarySearchTree();
    cout << "Adding elements: \n";
    bst = addElement(bst, "B");
    bst = addElement(bst, "A");
    bst = addElement(bst, "AB");
    bst = addElement(bst, "AA");
    printList(bst); cout << endl;
    cout << "Removal of AA: \n";
    bst = removeElement(bst, "AA");
    printList(bst); cout << endl;
    cout << "Search from A to B: \n";
    findElementsInRange(bst, "A", "B");
    cout << endl;

    // Демонстрация для АВЛ-дерева
    cout << "\nDemonstration of AVL-tree operation:\n";
    AVLNode* avlTree = createAVLTree();
    cout << "Adding elements: \n";
    avlTree = addElement(avlTree, "B");
    avlTree = addElement(avlTree, "A");
    avlTree = addElement(avlTree, "AB");
    avlTree = addElement(avlTree, "AA");
    printList(avlTree); cout << endl;
    cout << "Removal of AA: \n";
    avlTree = removeElement(avlTree, "AA");
    printList(avlTree); cout << endl;
    cout << "Search from A to B: \n";
    findElementsInRange(avlTree, "A", "B");
    cout << endl;

    // Демонстрация для 2-3 дерева
    cout << "\nDemonstration of the work of 2-3 trees:\n";
    TwoThreeNode* twoThreeTree = createTwoThreeTree();
    cout << "Adding elements: \n";
    twoThreeTree = addElement(twoThreeTree, "B");
    twoThreeTree = addElement(twoThreeTree, "A");
    twoThreeTree = addElement(twoThreeTree, "AB");
    twoThreeTree = addElement(twoThreeTree, "AA");
    printList(twoThreeTree); cout << endl;
    cout << "Search from A to B: \n";
    findElementsInRange(twoThreeTree, "A", "B");
}

void benchmarkMode() {
    Node* linkedList = createLinkedList();
    ArrayList arrayList = createArrayList();
    TreeNode* bst = createBinarySearchTree();
    AVLNode* avlTree = createAVLTree();
    TwoThreeNode* twoThreeTree = createTwoThreeTree();

    cout << "Benchmark for Linked List:\n";
    auto timeLL = measureTime(testLinkedList, linkedList);
    auto memoryLL = getMemoryUsage();
    cout << "Time: " << timeLL << " microseconds\n";
    cout << "Memory: " << memoryLL << " bytes\n\n";

    cout << "Benchmark for Array List:\n";
    auto timeAL = measureTime(testArrayList, arrayList);
    auto memoryAL = getMemoryUsage();
    cout << "Time: " << timeAL << " microseconds\n";
    cout << "Memory: " << memoryAL << " bytes\n\n";

    cout << "Benchmark for Binary Search Tree:\n";
    auto timeBST = measureTime(testBST, bst);
    auto memoryBST = getMemoryUsage();
    cout << "Time: " << timeBST << " microseconds\n";
    cout << "Memory: " << memoryBST << " bytes\n\n";

    cout << "Benchmark for AVL Tree:\n";
    auto timeAVL = measureTime(testAVLTree, avlTree);
    auto memoryAVL = getMemoryUsage();
    cout << "Time: " << timeAVL << " microseconds\n";
    cout << "Memory: " << memoryAVL << " bytes\n\n";

    cout << "Benchmark for 2-3 Tree:\n";
    auto timeTT = measureTime(testTwoThreeTree, twoThreeTree);
    auto memoryTT = getMemoryUsage();
    cout << "Time: " << timeTT << " microseconds\n";
    cout << "Memory: " << memoryTT << " bytes\n\n";
}
