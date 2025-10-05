#include <iostream>

int main() {
    double* pMatrix = nullptr;
    double* pVector = nullptr;
    double* pResult = nullptr;
    int Size = 0;

    std::cout << "Serial matrix-vector multiplication program" << std::endl;

    // === Task 2: input size ===
    do {
        std::cout << "Enter the size of the initial objects: ";
        std::cin >> Size;

        if (std::cin.fail() || Size <= 0) {
            std::cin.clear();
            std::cin.ignore(32767, '\n');
            std::cout << "Error: size must be a positive integer." << std::endl;
            Size = 0;
        }
    } while (Size <= 0);

    std::cout << "Chosen objects size = " << Size << std::endl;

    // === Task 3: allocate and initialize data ===
    pMatrix = new double[Size * Size];
    pVector = new double[Size];
    pResult = new double[Size];

    // Заповнення тестовими даними (можна змінити формулу, якщо потрібно інше)
    for (int i = 0; i < Size; i++) {
        for (int j = 0; j < Size; j++) {
            pMatrix[i * Size + j] = i + j + 1;  // приклад: матриця зі зростаючими числами
        }
        pVector[i] = 1.0; // простий вектор з одиниць
    }

    std::cout << "Initial data generated successfully." << std::endl;

    // Перевірочний висновок для малих розмірів (наприклад, <=5)
    if (Size <= 5) {
        std::cout << "Matrix:" << std::endl;
        for (int i = 0; i < Size; i++) {
            for (int j = 0; j < Size; j++) {
                std::cout << pMatrix[i * Size + j] << "\t";
            }
            std::cout << std::endl;
        }

        std::cout << "Vector:" << std::endl;
        for (int i = 0; i < Size; i++) {
            std::cout << pVector[i] << "\t";
        }
        std::cout << std::endl;
    }
    return 0;
}