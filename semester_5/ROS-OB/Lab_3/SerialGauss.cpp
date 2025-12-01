#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

// Глобальні змінні для зберігання позицій ведучих рядків
int *pSerialPivotPos; 
int *pSerialPivotIter;

// Функція для простої ініціалізації матриці та вектора (для налагодження)
void DummyDataInitialization(double* pMatrix, double* pVector, int Size) {
    int i, j;
    for (i = 0; i < Size; i++) {
        pVector[i] = i + 1;
        for (j = 0; j < Size; j++) {
            if (j <= i)
                pMatrix[i * Size + j] = 1;
            else
                pMatrix[i * Size + j] = 0;
        }
    }
}

// Функція для випадкової ініціалізації матриці та вектора
void RandomDataInitialization(double* pMatrix, double* pVector, int Size) {
    int i, j;
    srand(unsigned(clock()));
    for (i = 0; i < Size; i++) {
        pVector[i] = (rand() % 100) / 10.0;
        for (j = 0; j < Size; j++) {
            // Заповнюємо ВСЮ матрицю, прибираємо умову if (j <= i)
            pMatrix[i * Size + j] = (rand() % 100) / 10.0;
        }
    }
}
// Функція для виділення пам'яті та ініціалізації даних
void ProcessInitialization(double* &pMatrix, double* &pVector, double* &pResult, int &Size) {
    do {
        printf("\nEnter the size of the matrix and the vector: ");
        scanf("%d", &Size);
        printf("\nChosen size = %d \n", Size);
        if (Size <= 0)
            printf("\nSize of objects must be greater than 0!\n");
    } while (Size <= 0);

    // Виділення пам'яті
    pMatrix = new double[Size * Size];
    pVector = new double[Size];
    pResult = new double[Size];

    // Ініціалізація елементів (можна замінити на DummyDataInitialization для тестів)
    RandomDataInitialization(pMatrix, pVector, Size);
}

// Функція для форматованого виведення матриці
void PrintMatrix(double* pMatrix, int RowCount, int ColCount) {
    int i, j;
    for (i = 0; i < RowCount; i++) {
        for (j = 0; j < ColCount; j++)
            printf("%7.4f ", pMatrix[i * ColCount + j]);
        printf("\n");
    }
}

// Функція для форматованого виведення вектора
void PrintVector(double* pVector, int Size) {
    int i;
    for (i = 0; i < Size; i++)
        printf("%7.4f ", pVector[i]);
    printf("\n");
}

// Функція для пошуку ведучого рядка
int FindPivotRow(double* pMatrix, int Size, int Iter) {
    int PivotRow = -1; 
    double MaxValue = 0; 
    int i;

    for (i = 0; i < Size; i++) {
        if ((pSerialPivotIter[i] == -1) && (fabs(pMatrix[i * Size + Iter]) > MaxValue)) {
            PivotRow = i;
            MaxValue = fabs(pMatrix[i * Size + Iter]);
        }
    }
    return PivotRow;
}

// Функція для виключення стовпця
void SerialColumnElimination(double* pMatrix, double* pVector, int Pivot, int Iter, int Size) {
    double PivotValue, PivotFactor;
    PivotValue = pMatrix[Pivot * Size + Iter];
    for (int i = 0; i < Size; i++) {
        if (pSerialPivotIter[i] == -1) {
            PivotFactor = pMatrix[i * Size + Iter] / PivotValue;
            for (int j = Iter; j < Size; j++) {
                pMatrix[i * Size + j] -= PivotFactor * pMatrix[Pivot * Size + j];
            }
            pVector[i] -= PivotFactor * pVector[Pivot];
        }
    }
}

// Прямий хід методу Гауса
void SerialGaussianElimination(double* pMatrix, double* pVector, int Size) {
    int Iter;
    int PivotRow;
    for (Iter = 0; Iter < Size; Iter++) {
        PivotRow = FindPivotRow(pMatrix, Size, Iter);
        pSerialPivotPos[Iter] = PivotRow;
        pSerialPivotIter[PivotRow] = Iter;
        SerialColumnElimination(pMatrix, pVector, PivotRow, Iter, Size);
    }
}

// Зворотний хід методу Гауса
void SerialBackSubstitution(double* pMatrix, double* pVector, double* pResult, int Size) {
    int RowIndex, Row;
    for (int i = Size - 1; i >= 0; i--) {
        RowIndex = pSerialPivotPos[i];
        pResult[i] = pVector[RowIndex] / pMatrix[Size * RowIndex + i];
        for (int j = 0; j < i; j++) {
            Row = pSerialPivotPos[j];
            pVector[j] -= pMatrix[Row * Size + i] * pResult[i];
            pMatrix[Row * Size + i] = 0;
        }
    }
}

// Функція для виконання алгоритму Гауса
void SerialResultCalculation(double* pMatrix, double* pVector, double* pResult, int Size) {
    // Виділення пам'яті
    pSerialPivotPos = new int[Size];
    pSerialPivotIter = new int[Size];
    for (int i = 0; i < Size; i++) {
        pSerialPivotIter[i] = -1;
    }

    // Прямий хід
    SerialGaussianElimination(pMatrix, pVector, Size);
    // Зворотний хід
    SerialBackSubstitution(pMatrix, pVector, pResult, Size);

    // Звільнення пам'яті
    delete[] pSerialPivotPos;
    delete[] pSerialPivotIter;
}

// Функція для завершення обчислювального процесу
void ProcessTermination(double* pMatrix, double* pVector, double* pResult) {
    delete[] pMatrix;
    delete[] pVector;
    delete[] pResult;
}

int main() {
    double* pMatrix;
    double* pVector;
    double* pResult;
    int Size;
    time_t start, finish;
    double duration;

    printf("Serial Gauss algorithm for solving linear systems\n");

    // Виділення пам'яті та ініціалізація даних
    ProcessInitialization(pMatrix, pVector, pResult, Size);

    // Виведення матриці та вектора (можна закоментувати для великих розмірів)
    // printf("Initial Matrix \n");
    // PrintMatrix(pMatrix, Size, Size);
    // printf("Initial Vector \n");
    // PrintVector(pVector, Size);

    // Виконання алгоритму Гауса та замір часу
    start = clock();
    SerialResultCalculation(pMatrix, pVector, pResult, Size);
    finish = clock();
    duration = (finish - start) / double(CLOCKS_PER_SEC);

    // Виведення результату (можна закоментувати для великих розмірів)
    // printf("\n Result Vector: \n");
    // PrintVector(pResult, Size);

    // Виведення часу виконання
    printf("\n Time of execution: %f\n", duration);

    // Завершення процесу
    ProcessTermination(pMatrix, pVector, pResult);
    
    return 0;
}