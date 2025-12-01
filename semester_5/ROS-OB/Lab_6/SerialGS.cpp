#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>
#include <locale.h> // Виправлено підключення бібліотеки

// Функція для алгоритму Гаусса-Зейделя
void ResultCalculation(double* pMatrix, int Size, double& Eps, int& Iterations) {
    double dm, dmax, temp;
    int i, j; // Змінні циклу
    Iterations = 0;
    do {
        dmax = 0;
        for (i = 1; i < Size - 1; i++) {
            for (j = 1; j < Size - 1; j++) {
                temp = pMatrix[Size * i + j];
                pMatrix[Size * i + j] = 0.25 * (pMatrix[Size * (i + 1) + j] +
                                                pMatrix[Size * (i - 1) + j] +
                                                pMatrix[Size * i + j + 1] +
                                                pMatrix[Size * i + j - 1]);
                dm = fabs(pMatrix[Size * i + j] - temp);
                if (dmax < dm) dmax = dm;
            }
        }
        Iterations++;
    } while (dmax > Eps);
}

// Функція для завершення обчислювального процесу
void ProcessTermination(double* pMatrix) {
    delete[] pMatrix;
}

// Функція для форматованого виводу матриці
void PrintMatrix(double* pMatrix, int RowCount, int ColCount) {
    int i, j; // Змінні циклу
    for (i = 0; i < RowCount; i++) {
        for (j = 0; j < ColCount; j++) {
            printf("%7.4f ", pMatrix[i * ColCount + j]);
        }
        printf("\n");
    }
}

// Функція для простої ініціалізації значень вузлів сітки
void DummyDataInitialization(double* pMatrix, int Size) {
    int i, j; // Змінні циклу
    // Налаштування значень вузлів сітки
    for (i = 0; i < Size; i++) {
        for (j = 0; j < Size; j++) {
            if ((i == 0) || (i == Size - 1) || (j == 0) || (j == Size - 1))
                pMatrix[i * Size + j] = 100;
            else
                pMatrix[i * Size + j] = 0;
        }
    }
}

// Функція для виділення пам'яті та ініціалізації вузлів сітки
void ProcessInitialization(double*& pMatrix, int& Size, double& Eps) {
    // Налаштування розміру сітки
    do {
        printf("\nEnter the grid size: ");
        scanf("%d", &Size);
        printf("\nChosen grid size = %d", Size);
        if (Size <= 2)
            printf("\nSize of grid must be greater than 2!\n");
    } while (Size <= 2);

    // Налаштування необхідної точності
    do {
        printf("\nEnter the required accuracy: ");
        scanf("%lf", &Eps);
        printf("\nChosen accuracy = %lf", Eps);
        if (Eps <= 0)
            printf("\nAccuracy must be greater than 0!\n");
    } while (Eps <= 0);

    // Виділення пам'яті
    pMatrix = new double[Size * Size];
    // Налаштування значень вузлів сітки
    DummyDataInitialization(pMatrix, Size);
}

int main() {
    setlocale(LC_NUMERIC, "C"); // Примусове використання крапки для дробових чисел

    double* pMatrix;
    int Size;           // Розмір матриці
    double Eps;         // Необхідна точність
    int Iterations;     // Номер ітерації

    // Змінні для вимірювання часу
    clock_t start, finish;
    double duration;

    printf("Serial Gauss-Seidel algorithm\n");

    // Ініціалізація процесу
    ProcessInitialization(pMatrix, Size, Eps);

    // Вивід початкової матриці (можна закоментувати для великих розмірів)
    // printf("Initial Matrix: \n");
    // PrintMatrix(pMatrix, Size, Size);

    // Початок заміру часу
    start = clock();

    // Метод Гаусса-Зейделя
    ResultCalculation(pMatrix, Size, Eps, Iterations);

    // Кінець заміру часу
    finish = clock();
    duration = (double)(finish - start) / CLOCKS_PER_SEC;

    // Вивід результатів
    printf("\nNumber of iterations: %d\n", Iterations);
    printf("\nTime of execution: %f\n", duration);

    // Вивід результату (розкоментуй, якщо хочеш бачити матрицю в кінці)
    // printf("\nResult matrix: \n");
    // PrintMatrix(pMatrix, Size, Size);

    // Завершення обчислювального процесу
    ProcessTermination(pMatrix);
    
    return 0;
}