#include <iostream>
#include <vector>
#include <string>
#include <numeric>
#include <algorithm>
#include <unordered_set>
#include <iomanip>

// Клас для подання раціонального числа
class Rational {
    int numerator;
    int denominator;

public:
    // Конструктор з автоматичним скороченням дробу
    Rational(int n = 0, int d = 1) {
        if (d == 0) throw std::invalid_argument("Denominator cannot be zero!");
        int g = std::gcd(n, d);
        numerator = n / g;
        denominator = d / g;
        if (denominator < 0) {
            numerator *= -1;
            denominator *= -1;
        }
    }

    // Повертає числове значення дробу (double)
    double value() const {
        return static_cast<double>(numerator) / denominator;
    }

    // Перетворення в рядок у вигляді "a/b"
    std::string toString() const {
        return std::to_string(numerator) + "/" + std::to_string(denominator);
    }

    // Порівняння двох дробів
    bool operator==(const Rational& other) const {
        return numerator == other.numerator && denominator == other.denominator;
    }

    bool operator!=(const Rational& other) const {
        return !(*this == other);
    }
};

// Структура для універсального хешування з параметрами a, b, p, m
struct UniversalHash {
    int operator()(const Rational& r, int a, int b, int p, int m) const {
        long long x = static_cast<long long>(r.value() * 1e6); // Нормалізація
        return ((a * x + b) % p) % m;
    }
};

// Клас для представлення одного рядка в хеш-таблиці
struct HashRow {
    int a = 0, b = 0;        // Параметри хеш-функції
    int size = 0;            // Розмір підтаблиці
    Rational* table = nullptr; // Вказівник на масив раціональних чисел

    // Деструктор для очищення памʼяті
    ~HashRow() {
        delete[] table;
    }

    // Вивід вмісту рядка
    void print() const {
        std::cout << "a = " << a << " | b = " << b << " | size = " << size << "\n";
        for (int i = 0; i < size; ++i) {
            if (table[i] != Rational()) {
                std::cout << "[" << i << "]: " << table[i].toString() << "\n";
            }
        }
        std::cout << "------------------------------\n";
    }
};

// Клас, що реалізує ідеальне хешування для множини раціональних чисел
class PerfectHashTable {
    std::vector<std::vector<Rational>> buckets; // Перший рівень хешування
    std::vector<HashRow> secondLevel;           // Другий рівень — ідеальні рядки
    const int p = 10000019;                     // Просте число для хешування

public:
    // Побудова всієї хеш-таблиці
    void build(const std::vector<Rational>& values) {
        int m = values.size();
        buckets.resize(m);

        // --- Перший рівень хешування ---
        UniversalHash h1;
        int a1 = 31, b1 = 17;
        for (const auto& val : values) {
            int idx = h1(val, a1, b1, p, m);
            buckets[idx].push_back(val);
        }

        // --- Другий рівень хешування (перфектний) ---
        secondLevel.resize(m);
        for (int i = 0; i < m; ++i) {
            const auto& bucket = buckets[i];
            int sz = bucket.size();
            if (sz == 0) continue;

            int tableSize = sz * sz;
            secondLevel[i].size = tableSize;
            secondLevel[i].table = new Rational[tableSize];

            // Спроба підібрати параметри a, b без колізій
            bool success = false;
            for (int tries = 1; !success && tries < 1000; ++tries) {
                int a = rand() % (p - 1) + 1;
                int b = rand() % p;
                UniversalHash h2;
                std::vector<Rational> temp(tableSize);
                std::unordered_set<int> used;
                success = true;

                for (const auto& val : bucket) {
                    int idx = h2(val, a, b, p, tableSize);
                    if (used.count(idx)) {
                        success = false;
                        break;
                    }
                    used.insert(idx);
                    temp[idx] = val;
                }

                if (success) {
                    secondLevel[i].a = a;
                    secondLevel[i].b = b;
                    std::copy(temp.begin(), temp.end(), secondLevel[i].table);
                }
            }

            if (!success) {
                std::cerr << "Failed to find perfect hash for bucket " << i << "\n";
            }
        }
    }

    // Вивід усієї хеш-таблиці
    void print() const {
        for (int i = 0; i < secondLevel.size(); ++i) {
            if (secondLevel[i].size > 0) {
                std::cout << "=== Bucket " << i << " ===\n";
                secondLevel[i].print();
            }
        }
    }
};

// Точка входу
int main() {
    // Вхідна множина раціональних чисел
    std::vector<Rational> values = {
        Rational(1, 2), Rational(2, 3), Rational(3, 4), Rational(4, 5),
        Rational(5, 6), Rational(6, 7), Rational(7, 8), Rational(8, 9),
        Rational(9, 10), Rational(10, 11)
    };

    // Створення та побудова хеш-таблиці
    PerfectHashTable hashTable;
    hashTable.build(values);

    // Виведення хеш-таблиці в консоль
    hashTable.print();

    return 0;
}