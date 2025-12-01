#include <stdio.h>
#include <stdlib.h>
#include <time.h>

// Функція для простої ініціалізації елементів матриці
void DummyDataInitialization(double* pAMatrix, double* pBMatrix, int Size) {
    int i, j; // Змінні циклу
    for (i = 0; i < Size; i++) {
        for (j = 0; j < Size; j++) {
            pAMatrix[i * Size + j] = 1;
            pBMatrix[i * Size + j] = 1;
        }
    }
}

// Функція для випадкової ініціалізації елементів матриці
void RandomDataInitialization(double* pAMatrix, double* pBMatrix, int Size) {
    int i, j; // Змінні циклу
    srand(unsigned(clock()));
    for (i = 0; i < Size; i++) {
        for (j = 0; j < Size; j++) {
            pAMatrix[i * Size + j] = rand() / double(1000);
            pBMatrix[i * Size + j] = rand() / double(1000);
        }
    }
}

// Функція для виділення пам'яті та ініціалізації елементів матриці
void ProcessInitialization(double* &pAMatrix, double* &pBMatrix, double* &pCMatrix, int &Size) {
    // Встановлення розміру матриць
    do {
        printf("\nEnter the size of matrices: ");
        scanf("%d", &Size);
        printf("\nChosen matrices' size = %d\n", Size);
        if (Size <= 0)
            printf("\nSize of objects must be greater than 0!\n");
    } while (Size <= 0);

    // Виділення пам'яті
    pAMatrix = new double[Size * Size];
    pBMatrix = new double[Size * Size];
    pCMatrix = new double[Size * Size];

    // Ініціалізація елементів матриці
    RandomDataInitialization(pAMatrix, pBMatrix, Size);
    
    for (int i = 0; i < Size * Size; i++) {
        pCMatrix[i] = 0;
    }
}

// Функція для форматованого виводу матриці
void PrintMatrix(double* pMatrix, int RowCount, int ColCount) {
    int i, j; // Змінні циклу
    for (i = 0; i < RowCount; i++) {
        for (j = 0; j < ColCount; j++)
            printf("%7.4f ", pMatrix[i * RowCount + j]);
        printf("\n");
    }
}

// Функція для множення матриць
void SerialResultCalculation(double* pAMatrix, double* pBMatrix, double* pCMatrix, int Size) {
    int i, j, k; // Змінні циклу
    for (i = 0; i < Size; i++) {
        for (j = 0; j < Size; j++) {
            for (k = 0; k < Size; k++) {
                pCMatrix[i * Size + j] += pAMatrix[i * Size + k] * pBMatrix[k * Size + j];
            }
        }
    }
}

// Функція для завершення обчислювального процесу
void ProcessTermination(double* pAMatrix, double* pBMatrix, double* pCMatrix) {
    delete[] pAMatrix;
    delete[] pBMatrix;
    delete[] pCMatrix;
}

int main() {
    double* pAMatrix;  // Перший аргумент множення матриць
    double* pBMatrix;  // Другий аргумент множення матриць
    double* pCMatrix;  // Результуюча матриця
    int Size;          // Розмір матриць
    time_t start, finish;
    double duration;

    printf("Serial matrix multiplication program\n");

    // Виділення пам'яті та ініціалізація елементів матриці
    ProcessInitialization(pAMatrix, pBMatrix, pCMatrix, Size);

    // Вивід матриць (можна закоментувати для великих розмірів)
    printf("Initial A Matrix \n");
    PrintMatrix(pAMatrix, Size, Size);
    printf("Initial B Matrix \n");
    PrintMatrix(pBMatrix, Size, Size);

    // Множення матриць
    start = clock();
    SerialResultCalculation(pAMatrix, pBMatrix, pCMatrix, Size);
    finish = clock();
    duration = (finish - start) / double(CLOCKS_PER_SEC);

    // Вивід результуючої матриці (можна закоментувати для великих розмірів)
    printf("\n Result Matrix: \n");
    PrintMatrix(pCMatrix, Size, Size);

    // Вивід часу, витраченого на множення матриць
    printf("\n Time of execution: %f\n", duration);

    // Завершення обчислювального процесу
    ProcessTermination(pAMatrix, pBMatrix, pCMatrix);

    return 0;
}