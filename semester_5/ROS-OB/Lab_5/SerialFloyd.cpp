#include <cstdlib>
#include <cstdio>
#include <ctime>
#include <algorithm>

using namespace std;

// Прототип функції з SerialFloydTest.cpp
//void PrintMatrix(int* pMatrix, int RowCount, int ColCount);

const double InfinitiesPercent = 50.0;
const double RandomDataMultiplier = 10;

// Функція вибору мінімального значення
int Min(int A, int B) {
    int Result = (A < B) ? A : B;
    if ((A < 0) && (B >= 0)) Result = B;
    if ((B < 0) && (A >= 0)) Result = A;
    if ((A < 0) && (B < 0)) Result = -1;
    return Result;
}

// Попереднє оголошення функцій, що використовуються в main
void ProcessInitialization(int*& pMatrix, int& Size);
void ProcessTermination(int* pMatrix);
void DummyDataInitialization(int* pMatrix, int Size);
void RandomDataInitialization(int* pMatrix, int Size);
void SerialFloyd(int* pMatrix, int Size);

int main(int argc, char* argv[]) {
    int* pMatrix;       // Матриця суміжності
    int Size;           // Розмір матриці суміжності
    time_t start, finish;
    double duration = 0.0;

    printf("Serial Floyd algorithm\n");

    // Ініціалізація процесу
    ProcessInitialization(pMatrix, Size);

    //printf("The matrix before Floyd algorithm\n");
    //PrintMatrix(pMatrix, Size, Size);

    start = clock();

    // Послідовний алгоритм Флойда
    SerialFloyd(pMatrix, Size);

    finish = clock();

   // printf("The matrix after Floyd algorithm\n");
    //PrintMatrix(pMatrix, Size, Size);

    duration = (finish - start) / double(CLOCKS_PER_SEC);
    printf("Time of execution: %f\n", duration);

    // Завершення процесу
    ProcessTermination(pMatrix);

    return 0;
}

// Функція для виділення пам'яті та встановлення початкових значень
void ProcessInitialization(int*& pMatrix, int& Size) {
    do {
        printf("Enter the number of vertices: ");
        scanf("%d", &Size);
        if (Size <= 0)
            printf("The number of vertices should be greater then zero\n");
    } while (Size <= 0);

    printf("Using graph with %d vertices\n", Size);

    // Виділення пам'яті для матриці суміжності
    pMatrix = new int[Size * Size];

    // Ініціалізація даних (можна вибрати Dummy або Random)
    // DummyDataInitialization(pMatrix, Size);
    RandomDataInitialization(pMatrix, Size);
}

// Функція для завершення обчислювального процесу
void ProcessTermination(int* pMatrix) {
    delete[] pMatrix;
}

// Функція для простого встановлення початкових даних
void DummyDataInitialization(int* pMatrix, int Size) {
    for (int i = 0; i < Size; i++) {
        for (int j = i; j < Size; j++) {
            if (i == j)
                pMatrix[i * Size + j] = 0;
            else if (i == 0)
                pMatrix[i * Size + j] = j;
            else
                pMatrix[i * Size + j] = -1;

            pMatrix[j * Size + i] = pMatrix[i * Size + j];
        }
    }
}

// Функція для ініціалізації даних генератором випадкових чисел
void RandomDataInitialization(int* pMatrix, int Size) {
    srand((unsigned)time(0));
    for (int i = 0; i < Size; i++) {
        for (int j = 0; j < Size; j++) {
            if (i != j) {
                if ((rand() % 100) < InfinitiesPercent)
                    pMatrix[i * Size + j] = -1;
                else
                    pMatrix[i * Size + j] = rand() % 10 + 1;
            } else {
                pMatrix[i * Size + j] = 0;
            }
        }
    }
}

// Функція для послідовного алгоритму Флойда
void SerialFloyd(int* pMatrix, int Size) {
    int t1, t2;
    for (int k = 0; k < Size; k++) {
        for (int i = 0; i < Size; i++) {
            for (int j = 0; j < Size; j++) {
                if ((pMatrix[i * Size + k] != -1) && (pMatrix[k * Size + j] != -1)) {
                    t1 = pMatrix[i * Size + j];
                    t2 = pMatrix[i * Size + k] + pMatrix[k * Size + j];
                    pMatrix[i * Size + j] = Min(t1, t2);
                }
            }
        }
    }
}//
// Created by Matvii Liashenko on 01.12.2025.
//
