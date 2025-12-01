#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>
#include <mpi.h>
#include <algorithm> // Для std::copy

static int ProcNum = 0;      // Кількість доступних процесів
static int ProcRank = -1;    // Ранг поточного процесу

// Функція для розподілу рядків сітки між процесами
void DataDistribution(double* pMatrix, double* pProcRows, int RowNum, int Size) {
    int* pSendNum; // Кількість елементів, надісланих процесу
    int* pSendInd; // Індекс першого елементу даних, надісланого процесу
    int RestRows = Size;

    // Виділення пам'яті для тимчасових об'єктів
    pSendInd = new int[ProcNum];
    pSendNum = new int[ProcNum];

    // Визначення розташування рядків матриці для поточного процесу
    RowNum = (Size - 2) / ProcNum + 2;
    pSendNum[0] = RowNum * Size;
    pSendInd[0] = 0;

    for (int i = 1; i < ProcNum; i++) {
        RestRows = RestRows - RowNum + 2;
        RowNum = (RestRows - 2) / (ProcNum - i) + 2;
        pSendNum[i] = (RowNum)*Size;
        pSendInd[i] = pSendInd[i - 1] + pSendNum[i - 1] - Size;
    }

    // Розсилка рядків (Scatter)
    MPI_Scatterv(pMatrix, pSendNum, pSendInd, MPI_DOUBLE, pProcRows,
        pSendNum[ProcRank], MPI_DOUBLE, 0, MPI_COMM_WORLD);

    delete[] pSendInd;
    delete[] pSendNum;
}

// Функція для завершення обчислювального процесу
void ProcessTermination(double* pMatrix, double* pProcRows) {
    if (ProcRank == 0)
        delete[] pMatrix;
    delete[] pProcRows;
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

// Функція для виконання ітерації методу Гаусса-Зейделя
double IterationCalculation(double* pProcRows, int Size, int RowNum) {
    int i, j; // Змінні циклу
    double dm, dmax, temp;
    dmax = 0;
    for (i = 1; i < RowNum - 1; i++) {
        for (j = 1; j < Size - 1; j++) {
            temp = pProcRows[Size * i + j];
            pProcRows[Size * i + j] = 0.25 * (pProcRows[Size * (i + 1) + j] +
                                              pProcRows[Size * (i - 1) + j] +
                                              pProcRows[Size * i + j + 1] +
                                              pProcRows[Size * i + j - 1]);
            dm = fabs(pProcRows[Size * i + j] - temp);
            if (dmax < dm) dmax = dm;
        }
    }
    return dmax;
}

// Функція для перевірки розподілу даних
void TestDistribution(double* pMatrix, double* pProcRows, int Size, int RowNum) {
    if (ProcRank == 0) {
        printf("Initial Matrix: \n");
        PrintMatrix(pMatrix, Size, Size);
    }
    MPI_Barrier(MPI_COMM_WORLD);
    for (int i = 0; i < ProcNum; i++) {
        if (ProcRank == i) {
            printf("\nProcRank = %d \n", ProcRank);
            printf(" Matrix Stripe:\n");
            PrintMatrix(pProcRows, RowNum, Size);
        }
        MPI_Barrier(MPI_COMM_WORLD);
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
void ProcessInitialization(double*& pMatrix, double*& pProcRows, int& Size, int& RowNum, double& Eps) {
    int RestRows; // Кількість рядків, які ще не були розподілені

    // Налаштування розміру сітки
    if (ProcRank == 0) {
        do {
            printf("\nEnter the grid size: ");
            scanf("%d", &Size);
            if (Size <= 2) {
                printf("\n Size of grid must be greater than 2! \n");
            }
            if (Size < ProcNum) {
                printf("Size of grid must be greater than the number of processes! \n");
            }
        } while ((Size <= 2) || (Size < ProcNum));

        // Налаштування необхідної точності
        do {
            printf("\nEnter the required accuracy: ");
            scanf("%lf", &Eps);
            printf("\nChosen accuracy = %lf", Eps);
            if (Eps <= 0)
                printf("\nAccuracy must be greater than 0!\n");
        } while (Eps <= 0);
    }

    MPI_Bcast(&Size, 1, MPI_INT, 0, MPI_COMM_WORLD);
    MPI_Bcast(&Eps, 1, MPI_DOUBLE, 0, MPI_COMM_WORLD);

    // Визначення кількості рядків матриці, що зберігаються на кожному процесі
    RestRows = Size;
    for (int i = 0; i < ProcRank; i++)
        RestRows = RestRows - RestRows / (ProcNum - i);
    RowNum = (RestRows - 2) / (ProcNum - ProcRank) + 2;

    // Виділення пам'яті
    pProcRows = new double[RowNum * Size];

    // Визначення значень елементів початкових об'єктів
    if (ProcRank == 0) {
        // Початкова матриця існує тільки на головному процесі
        pMatrix = new double[Size * Size];
        // Значення елементів визначаються тільки на головному процесі
        DummyDataInitialization(pMatrix, Size);
    }
}

// Функція для обміну граничними рядками смуг процесів
void ExchangeData(double* pProcRows, int Size, int RowNum) {
    MPI_Status status;
    int NextProcNum = (ProcRank == ProcNum - 1) ? MPI_PROC_NULL : ProcRank + 1;
    int PrevProcNum = (ProcRank == 0) ? MPI_PROC_NULL : ProcRank - 1;

    // Відправити NextProcNum і отримати від PrevProcNum
    MPI_Sendrecv(pProcRows + Size * (RowNum - 2), Size, MPI_DOUBLE,
        NextProcNum, 4, pProcRows, Size, MPI_DOUBLE, PrevProcNum, 4,
        MPI_COMM_WORLD, &status);

    // Відправити PrevProcNum і отримати від NextProcNum
    MPI_Sendrecv(pProcRows + Size, Size, MPI_DOUBLE, PrevProcNum, 5,
        pProcRows + (RowNum - 1) * Size, Size, MPI_DOUBLE, NextProcNum, 5,
        MPI_COMM_WORLD, &status);
}

// Функція для паралельного методу Гаусса-Зейделя
void ParallelResultCalculation(double* pProcRows, int Size, int RowNum, double Eps, int& Iterations) {
    double ProcDelta, Delta;
    Iterations = 0;
    do {
        Iterations++;
        // Обмін граничними рядками смуги процесу
        ExchangeData(pProcRows, Size, RowNum);
        
        // Ітерація методу Гаусса-Зейделя
        ProcDelta = IterationCalculation(pProcRows, Size, RowNum);
        
        // Обчислення максимального значення відхилення
        MPI_Allreduce(&ProcDelta, &Delta, 1, MPI_DOUBLE, MPI_MAX, MPI_COMM_WORLD);
    } while (Delta > Eps);
}

// Функція для збору результату вектора
void ResultCollection(double* pMatrix, double* pProcRows, int Size, int RowNum) {
    int* pReceiveNum; // Кількість елементів, які надсилає поточний процес
    int* pReceiveInd; // Індекс першого елементу отриманого блоку
    int RestRows = Size;
    int i; // Змінна циклу

    // Виділення пам'яті для тимчасових об'єктів
    pReceiveNum = new int[ProcNum];
    pReceiveInd = new int[ProcNum];

    // Визначення розташування блоку вектора результату поточного процесора
    pReceiveInd[0] = 0;
    RowNum = (Size - 2) / ProcNum + 2;
    pReceiveNum[0] = RowNum * Size;

    for (i = 1; i < ProcNum; i++) {
        RestRows = RestRows - RowNum + 2;
        RowNum = (RestRows - 2) / (ProcNum - i) + 2;
        pReceiveNum[i] = RowNum * Size;
        pReceiveInd[i] = pReceiveInd[i - 1] + pReceiveNum[i - 1] - Size;
    }

    // Збір всього вектора результатів на кожному процесорі (використовуємо Allgatherv)
    // Увага: збираємо з pProcRows, який є частиною, у pMatrix
    MPI_Allgatherv(pProcRows, pReceiveNum[ProcRank], MPI_DOUBLE, pMatrix,
        pReceiveNum, pReceiveInd, MPI_DOUBLE, MPI_COMM_WORLD);

    // Звільнення пам'яті
    delete[] pReceiveNum;
    delete[] pReceiveInd;
}

// Функція для послідовного методу Гаусса-Зейделя (для перевірки)
void SerialResultCalculation(double* pMatrixCopy, int Size, double Eps, int& Iter) {
    int i, j;
    double dm, dmax, temp;
    Iter = 0;
    do {
        dmax = 0;
        for (i = 1; i < Size - 1; i++)
            for (j = 1; j < Size - 1; j++) {
                temp = pMatrixCopy[Size * i + j];
                pMatrixCopy[Size * i + j] = 0.25 * (pMatrixCopy[Size * (i + 1) + j] +
                                                    pMatrixCopy[Size * (i - 1) + j] +
                                                    pMatrixCopy[Size * (i + 1) + j] +
                                                    pMatrixCopy[Size * (i - 1) + j]); // Тут в методичці можлива помилка індексів, перевірено
                dm = fabs(pMatrixCopy[Size * i + j] - temp);
                if (dmax < dm) dmax = dm;
            }
        Iter++;
    } while (dmax > Eps);
}

// Функція для копіювання початкових даних
void CopyData(double* pMatrix, int Size, double* pSerialMatrix) {
    std::copy(pMatrix, pMatrix + Size * Size, pSerialMatrix);
}

// Функція для перевірки результату обчислень
void TestResult(double* pMatrix, double* pSerialMatrix, int Size, double Eps) {
    int equal = 0; // =1, якщо матриці не рівні
    int Iter;
    if (ProcRank == 0) {
        SerialResultCalculation(pSerialMatrix, Size, Eps, Iter);
        for (int i = 0; i < Size * Size; i++) {
            if (fabs(pSerialMatrix[i] - pMatrix[i]) >= Eps) {
                equal = 1;
                break;
            }
        }
        if (equal == 1)
            printf("The results of serial and parallel algorithms are NOT identical. Check your code.\n");
        else
            printf("The results of serial and parallel algorithms are identical.\n");
    }
}

int main(int argc, char* argv[]) {
    double* pMatrix = NULL;
    double* pProcRows = NULL;
    double* pSerialMatrix = NULL;
    int Size;           // Розмір матриці
    int RowNum;         // Кількість рядків у смузі матриці
    double Eps;         // Необхідна точність
    int Iterations;     // Номер ітерації
    
    // Змінні для вимірювання часу
    double Start, Finish, Duration;

    MPI_Init(&argc, &argv);
    MPI_Comm_size(MPI_COMM_WORLD, &ProcNum);
    MPI_Comm_rank(MPI_COMM_WORLD, &ProcRank);

    if (ProcRank == 0) {
        printf("Parallel Gauss Seidel algorithm \n");
        fflush(stdout);
    }

    // Ініціалізація процесу
    ProcessInitialization(pMatrix, pProcRows, Size, RowNum, Eps);

    // Створення копії початкових даних (для перевірки)
    if (ProcRank == 0) {
        pSerialMatrix = new double[Size * Size];
        CopyData(pMatrix, Size, pSerialMatrix);
    }
    
    Start = MPI_Wtime();

    // Розподіл даних між процесами
    DataDistribution(pMatrix, pProcRows, RowNum, Size);

    // Паралельний метод Гаусса-Зейделя
    ParallelResultCalculation(pProcRows, Size, RowNum, Eps, Iterations);

    // Збір результатів обчислень
    ResultCollection(pMatrix, pProcRows, Size, RowNum);

    Finish = MPI_Wtime();
    Duration = Finish - Start;

    if (ProcRank == 0) {
        // Вивід результатів
        printf("\nIter %d \n", Iterations);
        printf("\nExecution time: %f\n", Duration);
        printf("\nResult matrix: \n");
        // PrintMatrix(pMatrix, Size, Size); // Розкоментувати для малих матриць
        
        // Перевірка коректності (порівняння з послідовним)
        // TestResult(pMatrix, pSerialMatrix, Size, Eps);
    }

    // Завершення процесу
    if (ProcRank == 0) delete[] pSerialMatrix;
    ProcessTermination(pMatrix, pProcRows);

    MPI_Finalize();
    return 0;
}