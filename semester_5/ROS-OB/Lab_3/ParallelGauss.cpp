#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include <mpi.h>

int ProcNum; // Кількість доступних процесів
int ProcRank; // Ранг поточного процесу

// Глобальні змінні для відстеження ведучих рядків
int *pParallelPivotPos; 
int *pProcPivotIter;

int *pProcInd; // Індекси перших рядків на кожному процесі
int *pProcNum; // Кількість рядків на кожному процесі

// Функція для простої ініціалізації (тестові дані)
void DummyDataInitialization(double* pMatrix, double* pVector, int Size) {
    int i, j;
    for (i = 0; i < Size; i++) {
        pVector[i] = i + 1;
        for (j = 0; j < Size; j++) {
            if (j <= i) pMatrix[i * Size + j] = 1;
            else pMatrix[i * Size + j] = 0;
        }
    }
}

// Функція для випадкової ініціалізації
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
void ProcessInitialization(double* &pMatrix, double* &pVector, double* &pResult,
    double* &pProcRows, double* &pProcVector, double* &pProcResult,
    int &Size, int &RowNum) {
    
    int RestRows;
    int i;

    if (ProcRank == 0) {
        do {
            printf("\nEnter the size of the matrix and the vector: ");
            scanf("%d", &Size);
            if (Size < ProcNum) {
                printf("Size must be greater than number of processes! \n");
            }
        } while (Size < ProcNum);
    }
    
    // Розсилка розміру всім процесам
    MPI_Bcast(&Size, 1, MPI_INT, 0, MPI_COMM_WORLD);

    // Розрахунок кількості рядків для кожного процесу
    RestRows = Size;
    for (i = 0; i < ProcRank; i++)
        RestRows = RestRows - RestRows / (ProcNum - i);
    RowNum = RestRows / (ProcNum - ProcRank);

    // Виділення пам'яті під локальні частини
    pProcRows = new double[RowNum * Size];
    pProcVector = new double[RowNum];
    pProcResult = new double[RowNum];

    pParallelPivotPos = new int[Size];
    pProcPivotIter = new int[RowNum];

    pProcInd = new int[ProcNum];
    pProcNum = new int[ProcNum];

    for (int i = 0; i < RowNum; i++)
        pProcPivotIter[i] = -1;

    if (ProcRank == 0) {
        pMatrix = new double[Size * Size];
        pVector = new double[Size];
        pResult = new double[Size];
        // Генерація даних (можна замінити на DummyDataInitialization)
        RandomDataInitialization(pMatrix, pVector, Size);
    }
}

// Функція для розподілу даних між процесами
void DataDistribution(double* pMatrix, double* pProcRows, double* pVector,
    double* pProcVector, int Size, int RowNum) {
    
    int *pSendNum; // Кількість елементів для відправки
    int *pSendInd; // Індекс початку даних
    int RestRows = Size;
    
    // Виділення пам'яті під тимчасові масиви
    pSendInd = new int[ProcNum];
    pSendNum = new int[ProcNum];

    // Розрахунок розподілу рядків для MPI_Scatterv
    RowNum = (Size / ProcNum);
    pSendNum[0] = RowNum * Size;
    pSendInd[0] = 0;
    
    for (int i = 1; i < ProcNum; i++) {
        RestRows -= RowNum;
        RowNum = RestRows / (ProcNum - i);
        pSendNum[i] = RowNum * Size;
        pSendInd[i] = pSendInd[i - 1] + pSendNum[i - 1];
    }

    // Розсилка рядків матриці
    MPI_Scatterv(pMatrix, pSendNum, pSendInd, MPI_DOUBLE, pProcRows,
        pSendNum[ProcRank], MPI_DOUBLE, 0, MPI_COMM_WORLD);

    // Розрахунок розподілу вектора
    RestRows = Size;
    pProcInd[0] = 0;
    pProcNum[0] = Size / ProcNum;
    
    for (int i = 1; i < ProcNum; i++) {
        RestRows -= pProcNum[i - 1];
        pProcNum[i] = RestRows / (ProcNum - i);
        pProcInd[i] = pProcInd[i - 1] + pProcNum[i - 1];
    }

    MPI_Scatterv(pVector, pProcNum, pProcInd, MPI_DOUBLE, pProcVector,
        pProcNum[ProcRank], MPI_DOUBLE, 0, MPI_COMM_WORLD);

    delete[] pSendNum;
    delete[] pSendInd;
}

// Функція для збору результатів
void ResultCollection(double* pProcResult, double* pResult) {
    MPI_Gatherv(pProcResult, pProcNum[ProcRank], MPI_DOUBLE, pResult,
        pProcNum, pProcInd, MPI_DOUBLE, 0, MPI_COMM_WORLD);
}

// Функція для форматованого виведення матриці
void PrintMatrix(double* pMatrix, int RowCount, int ColCount) {
    for (int i = 0; i < RowCount; i++) {
        for (int j = 0; j < ColCount; j++)
            printf("%7.4f ", pMatrix[i * ColCount + j]);
        printf("\n");
    }
}

// Функція для форматованого виведення вектора
void PrintVector(double* pVector, int Size) {
    for (int i = 0; i < Size; i++)
        printf("%7.4f ", pVector[i]);
    printf("\n");
}

// Функція для виключення стовпців (локально)
void ParallelEliminateColumns(double* pProcRows, double* pProcVector,
    double* pPivotRow, int Size, int RowNum, int Iter) {
    
    double multiplier;
    for (int i = 0; i < RowNum; i++) {
        if (pProcPivotIter[i] == -1) {
            multiplier = pProcRows[i * Size + Iter] / pPivotRow[Iter];
            for (int j = Iter; j < Size; j++) {
                pProcRows[i * Size + j] -= pPivotRow[j] * multiplier;
            }
            pProcVector[i] -= pPivotRow[Size] * multiplier;
        }
    }
}

// Паралельний прямий хід методу Гауса
void ParallelGaussianElimination(double* pProcRows, double* pProcVector, int Size, int RowNum) {
    double MaxValue;
    int PivotPos;
    
    // Структура для пошуку максимуму MPI_MAXLOC
    struct { double MaxValue; int ProcRank; } ProcPivot, Pivot;

    double* pPivotRow = new double[Size + 1];

    for (int i = 0; i < Size; i++) {
        // Пошук локального ведучого рядка
        MaxValue = 0;
        PivotPos = -1;
        for (int j = 0; j < RowNum; j++) {
            if ((pProcPivotIter[j] == -1) && (MaxValue < fabs(pProcRows[j * Size + i]))) {
                MaxValue = fabs(pProcRows[j * Size + i]);
                PivotPos = j;
            }
        }
        
        ProcPivot.MaxValue = MaxValue;
        ProcPivot.ProcRank = ProcRank;

        // Пошук глобального ведучого процесу
        MPI_Allreduce(&ProcPivot, &Pivot, 1, MPI_DOUBLE_INT, MPI_MAXLOC, MPI_COMM_WORLD);

        // Якщо поточний процес має ведучий рядок
        if (ProcRank == Pivot.ProcRank) {
            pProcPivotIter[PivotPos] = i; // Запам'ятовуємо ітерацію
            pParallelPivotPos[i] = pProcInd[ProcRank] + PivotPos; // Глобальний індекс
        }
        
        // Розсилка інформації про позицію ведучого рядка
        MPI_Bcast(&pParallelPivotPos[i], 1, MPI_INT, Pivot.ProcRank, MPI_COMM_WORLD);

        if (ProcRank == Pivot.ProcRank) {
            // Копіювання ведучого рядка для розсилки
            for (int j = 0; j < Size; j++) {
                pPivotRow[j] = pProcRows[PivotPos * Size + j];
            }
            pPivotRow[Size] = pProcVector[PivotPos];
        }
        
        // Розсилка самого ведучого рядка
        MPI_Bcast(pPivotRow, Size + 1, MPI_DOUBLE, Pivot.ProcRank, MPI_COMM_WORLD);

        // Виключення стовпців
        ParallelEliminateColumns(pProcRows, pProcVector, pPivotRow, Size, RowNum, i);
    }
    delete[] pPivotRow;
}

// Допоміжна функція для знаходження власника рядка на зворотному ході
void FindBackPivotRow(int RowIndex, int &IterProcRank, int &IterPivotPos) {
    for (int i = 0; i < ProcNum - 1; i++) {
        if ((pProcInd[i] <= RowIndex) && (RowIndex < pProcInd[i + 1]))
            IterProcRank = i;
    }
    if (RowIndex >= pProcInd[ProcNum - 1])
        IterProcRank = ProcNum - 1;
    IterPivotPos = RowIndex - pProcInd[IterProcRank];
}

// Паралельний зворотний хід
void ParallelBackSubstitution(double* pProcRows, double* pProcVector,
    double* pProcResult, int Size, int RowNum) {
    
    int IterProcRank;
    int IterPivotPos;
    double IterResult;

    for (int i = Size - 1; i >= 0; i--) {
        // Визначення рангу процесу, що володіє потрібним рядком
        FindBackPivotRow(pParallelPivotPos[i], IterProcRank, IterPivotPos);

        if (ProcRank == IterProcRank) {
            IterResult = pProcVector[IterPivotPos] / pProcRows[IterPivotPos * Size + i];
            pProcResult[IterPivotPos] = IterResult;
        }

        // Розсилка знайденого значення невідомої
        MPI_Bcast(&IterResult, 1, MPI_DOUBLE, IterProcRank, MPI_COMM_WORLD);

        // Оновлення значень вектора b (правої частини)
        for (int j = 0; j < RowNum; j++) {
            if (pProcPivotIter[j] < i) {
                pProcVector[j] -= pProcRows[j * Size + i] * IterResult;
                pProcRows[j * Size + i] = 0;
            }
        }
    }
}

// Перевірка результату
void TestResult(double* pMatrix, double* pVector, double* pResult, int Size) {
    double* pRightPartVector;
    int equal = 0;
    double Accuracy = 1.e-6;

    if (ProcRank == 0) {
        pRightPartVector = new double[Size];
        for (int i = 0; i < Size; i++) {
            pRightPartVector[i] = 0;
            for (int j = 0; j < Size; j++) {
                pRightPartVector[i] += pMatrix[i * Size + j] * pResult[pParallelPivotPos[j]];
            }
        }
        for (int i = 0; i < Size; i++) {
            if (fabs(pRightPartVector[i] - pVector[i]) > Accuracy)
                equal = 1;
        }
        if (equal == 1)
            printf("The result of the parallel Gauss algorithm is NOT correct. Check your code.\n");
        else
            printf("The result of the parallel Gauss algorithm is correct.\n");
        
        delete[] pRightPartVector;
    }
}

// Основна функція розрахунку
void ParallelResultCalculation(double* pProcRows, double* pProcVector, double* pProcResult, int Size, int RowNum) {
    ParallelGaussianElimination(pProcRows, pProcVector, Size, RowNum);
    ParallelBackSubstitution(pProcRows, pProcVector, pProcResult, Size, RowNum);
}

// Звільнення пам'яті
void ProcessTermination(double* pMatrix, double* pVector, double* pResult,
    double* pProcRows, double* pProcVector, double* pProcResult) {
    if (ProcRank == 0) {
        delete[] pMatrix;
        delete[] pVector;
        delete[] pResult;
    }
    delete[] pProcRows;
    delete[] pProcVector;
    delete[] pProcResult;
    delete[] pParallelPivotPos;
    delete[] pProcPivotIter;
    delete[] pProcInd;
    delete[] pProcNum;
}

int main(int argc, char* argv[]) {
    double* pMatrix;
    double* pVector;
    double* pResult;
    double* pProcRows;
    double* pProcVector;
    double* pProcResult;
    int Size;
    int RowNum;
    double start, finish, duration;

    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &ProcRank);
    MPI_Comm_size(MPI_COMM_WORLD, &ProcNum);

    if (ProcRank == 0)
        printf("Parallel Gauss algorithm for solving linear systems\n");

    // Ініціалізація
    ProcessInitialization(pMatrix, pVector, pResult, pProcRows, pProcVector, pProcResult, Size, RowNum);

    start = MPI_Wtime();
    
    // Розподіл даних
    DataDistribution(pMatrix, pProcRows, pVector, pProcVector, Size, RowNum);
    
    // Виконання паралельного алгоритму
    ParallelResultCalculation(pProcRows, pProcVector, pProcResult, Size, RowNum);
    
    // Збір результатів
    ResultCollection(pProcResult, pResult);
    
    finish = MPI_Wtime();
    duration = finish - start;

    if (ProcRank == 0) {
        // Перевірка результату
        TestResult(pMatrix, pVector, pResult, Size);
        // Виведення часу виконання
        printf("\n Time of execution: %f\n", duration);
    }

    // Завершення процесу
    ProcessTermination(pMatrix, pVector, pResult, pProcRows, pProcVector, pProcResult);

    MPI_Finalize();
    return 0;
}