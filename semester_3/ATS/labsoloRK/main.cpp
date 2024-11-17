#include <iostream>
#include <vector>
#include <string>
#include <limits>

using namespace std;

// Функція для отримання символьної матриці від користувача
vector<vector<char>> getTextMatrix(int size) {
    vector<vector<char>> matrix(size, vector<char>(size));
    cout << "Enter characters for the text matrix (" << size << "x" << size << "):" << endl;
    for (int i = 0; i < size; i++) {
        for (int j = 0; j < size; j++) {
            cin >> matrix[i][j]; // Зчитування символу для кожної позиції в матриці
        }
    }
    return matrix;
}

// Функція для отримання зразка від користувача
vector<vector<char>> getPatternMatrix(int size) {
    vector<vector<char>> pattern(size, vector<char>(size));
    cout << "Enter characters for the pattern matrix (" << size << "x" << size << "):" << endl;
    for (int i = 0; i < size; i++) {
        for (int j = 0; j < size; j++) {
            cin >> pattern[i][j]; // Зчитування символу для кожної позиції в зразку
        }
    }
    return pattern;
}

// Хеш-функція для обчислення хешу рядка
unsigned long long computeRowHash(const vector<char>& row, int size) {
    unsigned long long hashValue = 0;
    int base = 256; // база для символів ASCII
    int prime = 101; // просте число для обмеження колізій
    for (int i = 0; i < size; i++) {
        hashValue = (hashValue * base + row[i]) % prime; // Обчислення хешу рядка
    }
    return hashValue;
}

// Узагальнений метод Рабіна-Карпа для пошуку зразка у текстовій матриці
pair<int, int> rabinKarp(const vector<vector<char>>& text, const vector<vector<char>>& pattern) {
    int n = text.size(); // Розмір текстової матриці
    int m = pattern.size(); // Розмір зразка
    unsigned long long patternHash = 0;
    vector<unsigned long long> patternRowHashes(m);

    // Обчислення хешу для кожного рядка у зразку
    for (int i = 0; i < m; i++) {
        patternRowHashes[i] = computeRowHash(pattern[i], m);
        patternHash += patternRowHashes[i]; // Сума хешів усіх рядків зразка
    }

    // Пошук зразка у текстовій матриці
    for (int i = 0; i <= n - m; i++) { // Проходження рядків текстової матриці
        for (int j = 0; j <= n - m; j++) { // Проходження стовпців текстової матриці
            unsigned long long textHash = 0;
            // Обчислення хешу для підматриці розміром m x m
            for (int k = 0; k < m; k++) {
                // Формування поточного рядка тексту для обчислення хешу
                vector<char> currentRow(text[i + k].begin() + j, text[i + k].begin() + j + m);
                textHash += computeRowHash(currentRow, m); // Додавання хешу рядка до загального хешу підматриці
            }

            // Перевірка на збіг хешів
            if (textHash == patternHash) {
                // Порівняння символів у разі збігу хешів для виключення помилкових збігів
                bool match = true;
                for (int x = 0; x < m && match; x++) {
                    for (int y = 0; y < m; y++) {
                        if (text[i + x][j + y] != pattern[x][y]) {
                            match = false; // Якщо хоча б один символ не співпадає, встановлюємо false
                            break;
                        }
                    }
                }
                if (match) {
                    return {i + 1, j + 1}; // Повернення позиції першого символу зразка (з урахуванням 1)
                }
            }
        }
    }

    return {-1, -1}; // Повернення значення, якщо зразок не знайдено
}

int main() {
    int n, m;
    cout << "Enter the size of the text matrix (n x n): ";
    cin >> n;
    // Перевірка коректності введення розміру текстової матриці
    while (cin.fail() || n <= 0) {
        cin.clear(); // Скидання стану cin
        cin.ignore(numeric_limits<streamsize>::max(), '\n'); // Очищення вхідного буфера
        cout << "Invalid input. Please enter a positive integer for the size of the text matrix: ";
        cin >> n;
    }

    cout << "Enter the size of the pattern matrix (m x m): ";
    cin >> m;
    // Перевірка коректності введення розміру зразка
    while (cin.fail() || m <= 0 || m > n) {
        cin.clear(); // Скидання стану cin
        cin.ignore(numeric_limits<streamsize>::max(), '\n'); // Очищення вхідного буфера
        cout << "Invalid input. Please enter a positive integer for the size of the pattern matrix (must be <= n): ";
        cin >> m;
    }

    vector<vector<char>> textMatrix = getTextMatrix(n); // Зчитування текстової матриці
    vector<vector<char>> patternMatrix = getPatternMatrix(m); // Зчитування зразка

    pair<int, int> result = rabinKarp(textMatrix, patternMatrix); // Виклик функції пошуку

    // Виведення результату
    if (result.first != -1) {
        cout << "Pattern found at position: row " << result.first << ", column " << result.second << endl;
    } else {
        cout << "Pattern not found in the text matrix." << endl;
    }

    return 0;
}
