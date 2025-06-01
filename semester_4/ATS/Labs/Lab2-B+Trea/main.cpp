#include <iostream>
#include <vector>
#include <cmath>
#include <memory>

using namespace std;

// Структура для зберігання комплексних чисел з цілими компонентами
// Порівняння: спочатку за модулем, при рівності — за дійсною частиною
struct ComplexInt {
    int real, imag;
    double mod;

    ComplexInt(int r = 0, int i = 0) : real(r), imag(i) {
        mod = sqrt(r * r + i * i);
    }

    bool operator<(const ComplexInt& other) const {
        if (mod == other.mod) return real < other.real;
        return mod < other.mod;
    }

    bool operator==(const ComplexInt& other) const {
        return real == other.real && imag == other.imag;
    }

    bool operator!=(const ComplexInt& other) const {
        return !(*this == other);
    }

    bool operator>(const ComplexInt& other) const {
        return other < *this;
    }

    bool operator<=(const ComplexInt& other) const {
        return *this < other || *this == other;
    }

    bool operator>=(const ComplexInt& other) const {
        return *this > other || *this == other;
    }

    friend ostream& operator<<(ostream& os, const ComplexInt& c) {
        os << c.real << (c.imag >= 0 ? "+" : "") << c.imag << "i";
        return os;
    }
};

// Клас вузла B+ дерева — містить ключі, нащадків, та зв'язки між листами
template<typename T>
struct BPlusNode {
    bool leaf;
    unsigned size;
    vector<T> data;
    vector<shared_ptr<BPlusNode>> children;
    shared_ptr<BPlusNode> next_leaf, prev_leaf, parent;

    BPlusNode() : leaf(false), size(0) {}
};

// Клас B+ дерева — реалізує основні операції: вставку, видалення, вивід
template<typename T>
class BPlusTree {
    using Node = shared_ptr<BPlusNode<T>>;
    Node root;
    unsigned min_degree, min_fill, max_fill;

    // Пошук ключа у піддереві, повертає вузол і позицію, якщо знайдено
    Node subtree_search(Node node, const T& key, unsigned& index) {
        if (node->leaf) {
            auto it = find(node->data.begin(), node->data.end(), key);
            index = distance(node->data.begin(), it);
            return (it != node->data.end()) ? node : nullptr;
        }
        unsigned i = 0;
        while (i < node->size && key >= node->data[i]) i++;
        return subtree_search(node->children[i], key, index);
    }

    // Розділення вузла при переповненні
    void split_node(Node node) {
        unsigned mid = node->size / 2;
        Node new_node = make_shared<BPlusNode<T>>();
        new_node->leaf = node->leaf;
        new_node->data.assign(node->data.begin() + mid, node->data.end());
        new_node->children.assign(node->children.begin() + (node->leaf ? 0 : mid + 1), node->children.end());
        new_node->size = new_node->data.size();
        node->data.resize(mid);
        node->children.resize(node->leaf ? 0 : mid + 1);
        node->size = mid;

        if (node->leaf) {
            new_node->next_leaf = node->next_leaf;
            if (node->next_leaf) node->next_leaf->prev_leaf = new_node;
            node->next_leaf = new_node;
            new_node->prev_leaf = node;
        }

        if (!node->parent) {
            Node new_root = make_shared<BPlusNode<T>>();
            new_root->leaf = false;
            new_root->data.push_back(new_node->data[0]);
            new_root->children = { node, new_node };
            root = new_root;
            node->parent = new_root;
            new_node->parent = new_root;
            new_root->size = 1;
        } else {
            Node p = node->parent;
            T promote = new_node->data[0];
            auto it = upper_bound(p->data.begin(), p->data.end(), promote);
            int pos = distance(p->data.begin(), it);
            p->data.insert(it, promote);
            p->children.insert(p->children.begin() + pos + 1, new_node);
            p->size++;
            new_node->parent = p;
            if (p->size > max_fill) split_node(p);
        }
    }

    // Вставка ключа у піддерево
    void subtree_insert(Node node, const T& key) {
        if (node->leaf) {
            auto it = upper_bound(node->data.begin(), node->data.end(), key);
            node->data.insert(it, key);
            node->size++;
            if (node->size > max_fill) split_node(node);
        } else {
            unsigned i = 0;
            while (i < node->size && key >= node->data[i]) i++;
            subtree_insert(node->children[i], key);
        }
    }

public:
    BPlusTree(unsigned d = 2) {
        min_degree = max(2u, d);
        min_fill = min_degree - 1;
        max_fill = 2 * min_degree - 1;
        root = make_shared<BPlusNode<T>>();
        root->leaf = true;
    }

    void insert(const T& key) {
        subtree_insert(root, key);
    }

    // Вивід структури дерева у консоль (рекурсивно)
    void print(ostream& out) {
        function<void(Node,int)> dfs = [&](Node node, int lvl) {
            out << string(lvl * 2, ' ') << "Node (" << (node->leaf ? "leaf" : "internal") << ") size=" << node->size << "\n";
            for (const auto& el : node->data)
                out << string(lvl * 2 + 2, ' ') << el << "\n";
            if (!node->leaf)
                for (auto& child : node->children) dfs(child, lvl + 1);
        };
        dfs(root, 0);
    }

    // Вивід усіх ключів у відсортованому порядку (обхід листків)
    void printSorted(ostream& out) {
        Node ptr = root;
        while (!ptr->leaf) ptr = ptr->children[0];
        int i = 1;
        while (ptr) {
            for (auto& el : ptr->data)
                out << i++ << ") " << el << "\n";
            ptr = ptr->next_leaf;
        }
    }

    // Видалення ключа з дерева (з листка)
    void remove(const T& key) {
        unsigned idx = 0;
        Node node = subtree_search(root, key, idx);
        if (!node) return;
        node->data.erase(node->data.begin() + idx);
        node->size--;
        // Повна реалізація rebalance — опціональна для цього варіанту
    }
};

// Основна функція для демонстрації роботи B+ дерева з комплексними числами
// Містить текстове меню для вставки, видалення, виводу
void example_ComplexInt() {
    BPlusTree<ComplexInt> tree(3);
    int choice = -1;

    while (choice != 0) {
        cout << "\n====== MENU ======\n";
        cout << "1. Insert complex number\n";
        cout << "2. Remove complex number\n";
        cout << "3. Print tree\n";
        cout << "4. Print sorted values\n";
        cout << "0. Exit\n";
        cout << "Enter choice: ";
        cin >> choice;

        if (choice == 1) {
            int r, im;
            cout << "Enter real and imaginary part: ";
            cin >> r >> im;
            tree.insert(ComplexInt(r, im));
            cout << "Inserted: " << ComplexInt(r, im) << "\n";
        } else if (choice == 2) {
            int r, im;
            cout << "Enter real and imaginary part to remove: ";
            cin >> r >> im;
            tree.remove(ComplexInt(r, im));
            cout << "Removed: " << ComplexInt(r, im) << "\n";
        } else if (choice == 3) {
            cout << "\nTree structure:\n";
            tree.print(cout);
        } else if (choice == 4) {
            cout << "\nSorted list:\n";
            tree.printSorted(cout);
        } else if (choice == 0) {
            cout << "Exiting...\n";
        } else {
            cout << "Invalid choice!\n";
        }
    }
}

int main() {
    example_ComplexInt();
    return 0;
}