// Реалізація дерева порядкової статистики на основі червоно-чорного дерева
// Тип елементів: комплексні числа з цілочисельними компонентами

#include <iostream>
#include <cmath>
#include <string>
#include <limits>
#include <iomanip>
using namespace std;

// Клас, що описує комплексні числа з цілочисельними компонентами
class ComplexInt {
public:
    int real, imag;
    ComplexInt(int r = 0, int i = 0) : real(r), imag(i) {}

    // Обчислення модуля комплексного числа
    double modulus() const {
        return sqrt(real * real + imag * imag);
    }

    // Порівняння: спочатку за модулем, потім за дійсною частиною
    bool operator<(const ComplexInt& other) const {
        double m1 = this->modulus();
        double m2 = other.modulus();
        if (m1 != m2) return m1 < m2;
        return real < other.real;
    }

    bool operator==(const ComplexInt& other) const {
        return real == other.real && imag == other.imag;
    }

    friend ostream& operator<<(ostream& os, const ComplexInt& c) {
        os << c.real << (c.imag >= 0 ? "+" : "") << c.imag << "i";
        return os;
    }
};

// Вузол червоно-чорного дерева
struct Node {
    ComplexInt value;
    Node *left, *right, *parent;
    char color; // 'R' або 'B'
    int size;   // розмір піддерева

    Node(const ComplexInt& val) : value(val), left(nullptr), right(nullptr), parent(nullptr), color('R'), size(1) {}
};

// Червоний-чорний дерево з підтримкою порядкової статистики
class OrderStatisticRBTree {
private:
    Node* root = nullptr;

    // Оновлення розміру піддерева
    void updateSize(Node* n) {
        if (n) n->size = 1 + getSize(n->left) + getSize(n->right);
    }

    // Рекурсивне оновлення size вгору до кореня
    void updateSizeUp(Node* n) {
        while (n) {
            updateSize(n);
            n = n->parent;
        }
    }

    // Отримати size вузла
    int getSize(Node* n) {
        return n ? n->size : 0;
    }

    // Лівий поворот
    void leftRotate(Node* x) {
        Node* y = x->right;
        x->right = y->left;
        if (y->left) y->left->parent = x;
        y->parent = x->parent;
        if (!x->parent) root = y;
        else if (x == x->parent->left) x->parent->left = y;
        else x->parent->right = y;
        y->left = x;
        x->parent = y;
        updateSize(x);
        updateSize(y);
    }

    // Правий поворот
    void rightRotate(Node* y) {
        Node* x = y->left;
        y->left = x->right;
        if (x->right) x->right->parent = y;
        x->parent = y->parent;
        if (!y->parent) root = x;
        else if (y == y->parent->left) y->parent->left = x;
        else y->parent->right = x;
        x->right = y;
        y->parent = x;
        updateSize(y);
        updateSize(x);
    }

    // Балансування після вставки
    void insertFixup(Node* z) {
        while (z->parent && z->parent->color == 'R') {
            Node* gp = z->parent->parent;
            if (z->parent == gp->left) {
                Node* y = gp->right;
                if (y && y->color == 'R') {
                    z->parent->color = y->color = 'B';
                    gp->color = 'R';
                    z = gp;
                } else {
                    if (z == z->parent->right) {
                        z = z->parent;
                        leftRotate(z);
                    }
                    z->parent->color = 'B';
                    gp->color = 'R';
                    rightRotate(gp);
                }
            } else {
                Node* y = gp->left;
                if (y && y->color == 'R') {
                    z->parent->color = y->color = 'B';
                    gp->color = 'R';
                    z = gp;
                } else {
                    if (z == z->parent->left) {
                        z = z->parent;
                        rightRotate(z);
                    }
                    z->parent->color = 'B';
                    gp->color = 'R';
                    leftRotate(gp);
                }
            }
        }
        root->color = 'B';
    }

    // Вставка вузла у дерево
    void insert(Node*& root, Node* z) {
        Node* y = nullptr;
        Node* x = root;
        while (x) {
            y = x;
            x = (z->value < x->value) ? x->left : x->right;
        }
        z->parent = y;
        if (!y) root = z;
        else if (z->value < y->value) y->left = z;
        else y->right = z;

        updateSizeUp(z);
        insertFixup(z);
    }

    // Вивід дерева у вигляді гілок
    void printTree(Node* node, string indent = "", bool last = true) {
        if (node) {
            cout << indent;
            if (last) {
                cout << "└─";
                indent += "  ";
            } else {
                cout << "├─";
                indent += "│ ";
            }
            cout << (node->color == 'R' ? "[R] " : "[B] ") << node->value << " (size=" << node->size << ")" << endl;
            printTree(node->left, indent, false);
            printTree(node->right, indent, true);
        }
    }

    // Пошук k-го за порядком елемента
    ComplexInt* select(Node* x, int k) {
        if (!x) return nullptr;
        int leftSize = getSize(x->left);
        if (k == leftSize + 1) return &x->value;
        else if (k <= leftSize) return select(x->left, k);
        else return select(x->right, k - leftSize - 1);
    }

public:
    void insert(const ComplexInt& val) {
        Node* z = new Node(val);
        insert(root, z);
    }

    void printInorder() {
        if (!root) cout << "Tree is empty.\n";
        else printTree(root);
    }

    ComplexInt* getKth(int k) {
        return select(root, k);
    }
};

int main() {
    OrderStatisticRBTree tree;
    int cmd;

    while (true) {
        cout << "1 - Insert complex number\n2 - Print tree\n3 - Get k-th element\n0 - Exit\n> ";
        cin >> cmd;
        if (cmd == 0) break;
        if (cmd == 1) {
            int r, i;
            cout << "Enter real and imaginary parts: ";
            cin >> r >> i;
            tree.insert(ComplexInt(r, i));
        } else if (cmd == 2) {
            tree.printInorder();
        } else if (cmd == 3) {
            int k;
            cout << "Enter k: ";
            cin >> k;
            ComplexInt* res = tree.getKth(k);
            if (res) cout << "k-th element: " << *res << endl;
            else cout << "Invalid k!\n";
        }
    }
    return 0;
}