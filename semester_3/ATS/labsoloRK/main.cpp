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
            cin >> matrix[i][j];
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
            cin >> pattern[i][j];
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
        hashValue = (hashValue * base + row[i]) % prime;
    }
    return hashValue;
}

// Узагальнений метод Рабіна-Карпа
pair<int, int> rabinKarp(const vector<vector<char>>& text, const vector<vector<char>>& pattern) {
    int n = text.size();
    int m = pattern.size();
    unsigned long long patternHash = 0;
    vector<unsigned long long> patternRowHashes(m);

    // Обчислення хешу для кожного рядка у зразку
    for (int i = 0; i < m; i++) {
        patternRowHashes[i] = computeRowHash(pattern[i], m);
        patternHash += patternRowHashes[i];
    }

    // Пошук зразка у текстовій матриці
    for (int i = 0; i <= n - m; i++) {
        for (int j = 0; j <= n - m; j++) {
            unsigned long long textHash = 0;
            // Обчислення хешу для підматриці розміром m x m
            for (int k = 0; k < m; k++) {
                vector<char> currentRow(text[i + k].begin() + j, text[i + k].begin() + j + m);
                textHash += computeRowHash(currentRow, m);
            }

            // Перевірка на співпадіння
            if (textHash == patternHash) {
                // Порівняння символів
                bool match = true;
                for (int x = 0; x < m && match; x++) {
                    for (int y = 0; y < m; y++) {
                        if (text[i + x][j + y] != pattern[x][y]) {
                            match = false;
                            break;
                        }
                    }
                }
                if (match) {
                    return {i + 1, j + 1}; // Додаємо 1 для правильного підрахунку
                }
            }
        }
    }

    return {-1, -1}; // Якщо зразок не знайдено
}

int main() {
    int n, m;
    cout << "Enter the size of the text matrix (n x n): ";
    cin >> n;
    while (cin.fail() || n <= 0) {
        cin.clear(); // Скидання стану cin
        cin.ignore(numeric_limits<streamsize>::max(), '\n'); // Очищення вхідного буфера
        cout << "Invalid input. Please enter a positive integer for the size of the text matrix: ";
        cin >> n;
    }

    cout << "Enter the size of the pattern matrix (m x m): ";
    cin >> m;
    while (cin.fail() || m <= 0 || m > n) {
        cin.clear(); // Скидання стану cin
        cin.ignore(numeric_limits<streamsize>::max(), '\n'); // Очищення вхідного буфера
        cout << "Invalid input. Please enter a positive integer for the size of the pattern matrix (must be <= n): ";
        cin >> m;
    }

    vector<vector<char>> textMatrix = getTextMatrix(n);
    vector<vector<char>> patternMatrix = getPatternMatrix(m);

    pair<int, int> result = rabinKarp(textMatrix, patternMatrix);

    if (result.first != -1) {
        cout << "Pattern found at position: row " << result.first << ", column " << result.second << endl;
    } else {
        cout << "Pattern not found in the text matrix." << endl;
    }

    return 0;
}
