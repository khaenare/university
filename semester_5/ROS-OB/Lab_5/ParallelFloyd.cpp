#include <cstdlib>
#include <cstdio>
#include <ctime>
#include <algorithm>
#include <mpi.h>

using namespace std;

// Прототипи функцій з ParallelFloydTest.cpp
void CopyMatrix(int* pMatrix, int Size, int* pMatrixCopy);
bool CompareMatrices(int* pMatrix1, int* pMatrix2, int Size);
void SerialFloyd(int* pMatrix, int Size);
//void PrintMatrix(int* pMatrix, int RowCount, int ColCount);

int ProcRank; // Ранг поточного процесу
int ProcNum;  // Кількість процесів

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

// Попереднє оголошення локальних функцій
void ProcessInitialization(int*& pMatrix, int*& pProcRows, int& Size, int& RowNum);
void ProcessTermination(int* pMatrix, int* pProcRows);
void DummyDataInitialization(int* pMatrix, int Size);
void RandomDataInitialization(int* pMatrix, int Size);
void DataDistribution(int* pMatrix, int* pProcRows, int Size, int RowNum);
void ResultCollection(int* pMatrix, int* pProcRows, int Size, int RowNum);
void ParallelFloyd(int* pProcRows, int Size, int RowNum);
void RowDistribution(int* pProcRows, int Size, int RowNum, int k, int* pRow);
void TestResult(int* pMatrix, int* pSerialMatrix, int Size);

int main(int argc, char* argv[]) {
    int* pMatrix = 0;   // Матриця суміжності
    int Size;           // Розмір матриці суміжності
    int* pProcRows = 0; // Рядки процесу
    int RowNum;         // Кількість рядків процесу
    double start, finish;
    double duration = 0.0;
    int* pSerialMatrix = 0;

    MPI_Init(&argc, &argv);
    MPI_Comm_size(MPI_COMM_WORLD, &ProcNum);
    MPI_Comm_rank(MPI_COMM_WORLD, &ProcRank);

    if (ProcRank == 0)
        printf("Parallel Floyd algorithm\n");

    // Ініціалізація процесу
    ProcessInitialization(pMatrix, pProcRows, Size, RowNum);

    if (ProcRank == 0) {
        // Копіювання матриці для тестування
        pSerialMatrix = new int[Size * Size];
        CopyMatrix(pMatrix, Size, pSerialMatrix);
    }

    start = MPI_Wtime();

    // Розподіл початкових даних між процесами
    DataDistribution(pMatrix, pProcRows, Size, RowNum);

    // Паралельний алгоритм Флойда
    ParallelFloyd(pProcRows, Size, RowNum);

    // Збір даних процесу
    ResultCollection(pMatrix, pProcRows, Size, RowNum);

    finish = MPI_Wtime();

    // Тестування результату
    TestResult(pMatrix, pSerialMatrix, Size);

    duration = finish - start;
    if (ProcRank == 0) {
        printf("Time of execution: %f\n", duration);
    }

    if (ProcRank == 0)
        delete[] pSerialMatrix;

    // Завершення процесу
    ProcessTermination(pMatrix, pProcRows);

    MPI_Finalize();
    return 0;
}

// Функція для виділення пам'яті та встановлення початкових значень
void ProcessInitialization(int*& pMatrix, int*& pProcRows, int& Size, int& RowNum) {
    if (ProcRank == 0) {
        do {
            printf("Enter the number of vertices: ");
            scanf("%d", &Size);
            if (Size < ProcNum)
                printf("The number of vertices should be greater then the number of processes\n");
        } while (Size < ProcNum);
        printf("Using the graph with %d vertices\n", Size);
    }

    // Розсилка кількості вершин
    MPI_Bcast(&Size, 1, MPI_INT, 0, MPI_COMM_WORLD);

    // Кількість рядків для кожного процесу
    int RestRows = Size;
    for (int i = 0; i < ProcRank; i++)
        RestRows = RestRows - RestRows / (ProcNum - i);
    RowNum = RestRows / (ProcNum - ProcRank);

    // Виділення пам'яті для рядків поточного процесу
    pProcRows = new int[Size * RowNum];

    if (ProcRank == 0) {
        // Виділення пам'яті для матриці суміжності
        pMatrix = new int[Size * Size];
        // Ініціалізація даних
        // DummyDataInitialization(pMatrix, Size);
        RandomDataInitialization(pMatrix, Size);
    }
}

// Функція для завершення обчислювального процесу
void ProcessTermination(int* pMatrix, int* pProcRows) {
    if (ProcRank == 0)
        delete[] pMatrix;
    delete[] pProcRows;
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

// Функція для встановлення даних генератором випадкових чисел
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

// Функція для розподілу даних між процесами
void DataDistribution(int* pMatrix, int* pProcRows, int Size, int RowNum) {
    int* pSendNum; // Кількість елементів, надісланих процесу
    int* pSendInd; // Індекс першого елемента даних, надісланого процесу
    int RestRows = Size; // Кількість рядків, які ще не розподілені

    // Виділення пам'яті для тимчасових об'єктів
    pSendInd = new int[ProcNum];
    pSendNum = new int[ProcNum];

    // Визначення розташування рядків матриці для поточного процесу
    int CurrentRowNum = Size / ProcNum;
    pSendNum[0] = CurrentRowNum * Size;
    pSendInd[0] = 0;

    for (int i = 1; i < ProcNum; i++) {
        RestRows -= CurrentRowNum;
        CurrentRowNum = RestRows / (ProcNum - i);
        pSendNum[i] = CurrentRowNum * Size;
        pSendInd[i] = pSendInd[i - 1] + pSendNum[i - 1];
    }

    // Розсилка рядків (Scatter)
    MPI_Scatterv(pMatrix, pSendNum, pSendInd, MPI_INT,
                 pProcRows, pSendNum[ProcRank], MPI_INT, 0, MPI_COMM_WORLD);

    // Звільнення виділеної пам'яті
    delete[] pSendNum;
    delete[] pSendInd;
}

// Функція для збору результатів процесу
void ResultCollection(int* pMatrix, int* pProcRows, int Size, int RowNum) {
    int* pReceiveNum; // Кількість елементів, які надсилає поточний процес
    int* pReceiveInd; // Зміщення для зберігання даних від поточного процесу
    int RestRows = Size; // Кількість рядків, які ще не зібрані

    // Виділення пам'яті для тимчасових об'єктів
    pReceiveNum = new int[ProcNum];
    pReceiveInd = new int[ProcNum];

    // Визначення розташування блоку даних результату поточного процесу
    int CurrentRowNum = Size / ProcNum;
    pReceiveInd[0] = 0;
    pReceiveNum[0] = CurrentRowNum * Size;

    for (int i = 1; i < ProcNum; i++) {
        RestRows -= CurrentRowNum;
        CurrentRowNum = RestRows / (ProcNum - i);
        pReceiveNum[i] = CurrentRowNum * Size;
        pReceiveInd[i] = pReceiveInd[i - 1] + pReceiveNum[i - 1];
    }

    // Збір усієї матриці на процесі 0
    MPI_Gatherv(pProcRows, pReceiveNum[ProcRank], MPI_INT,
                pMatrix, pReceiveNum, pReceiveInd, MPI_INT, 0, MPI_COMM_WORLD);

    // Звільнення виділеної пам'яті
    delete[] pReceiveNum;
    delete[] pReceiveInd;
}

// Функція для розсилки рядків між усіма процесами
void RowDistribution(int* pProcRows, int Size, int RowNum, int k, int* pRow) {
    int ProcRowRank; // Ранг процесу з рядком k
    int ProcRowNum;  // Номер рядка процесу

    // Пошук рангу процесу з рядком k
    int RestRows = Size;
    int Ind = 0;
    int Num = Size / ProcNum;

    for (ProcRowRank = 1; ProcRowRank < ProcNum + 1; ProcRowRank++) {
        if (k < Ind + Num) break;
        RestRows -= Num;
        Ind += Num;
        Num = RestRows / (ProcNum - ProcRowRank);
    }
    ProcRowRank = ProcRowRank - 1;
    ProcRowNum = k - Ind;

    if (ProcRowRank == ProcRank) {
        // Копіювання рядка в масив pRow
        copy(&pProcRows[ProcRowNum * Size], &pProcRows[(ProcRowNum + 1) * Size], pRow);
    }

    // Розсилка рядка всім процесам
    MPI_Bcast(pRow, Size, MPI_INT, ProcRowRank, MPI_COMM_WORLD);
}

// Функція для паралельного алгоритму Флойда
void ParallelFloyd(int* pProcRows, int Size, int RowNum) {
    int* pRow = new int[Size];
    int t1, t2;

    for (int k = 0; k < Size; k++) {
        // Розподіл рядка між усіма процесами
        RowDistribution(pProcRows, Size, RowNum, k, pRow);

        // Оновлення елементів матриці суміжності
        for (int i = 0; i < RowNum; i++) {
            for (int j = 0; j < Size; j++) {
                if ((pProcRows[i * Size + k] != -1) && (pRow[j] != -1)) {
                    t1 = pProcRows[i * Size + j];
                    t2 = pProcRows[i * Size + k] + pRow[j];
                    pProcRows[i * Size + j] = Min(t1, t2);
                }
            }
        }
    }
    delete[] pRow;
}

// Функція для форматованого виводу всіх смуг
//void ParallelPrintMatrix(int* pProcRows, int Size, int RowNum) {
    //for (int i = 0; i < ProcNum; i++) {
        //MPI_Barrier(MPI_COMM_WORLD);
        //if (ProcRank == i) {
           // printf("ProcRank = %d\n", ProcRank);
            //fflush(stdout);
            //printf("Proc rows:\n");
            //fflush(stdout);
            //PrintMatrix(pProcRows, RowNum, Size);
            //fflush(stdout);
       // }
        //MPI_Barrier(MPI_COMM_WORLD);
   // }
//}

// Функція для тестування розподілу даних
void TestDistribution(int* pMatrix, int* pProcRows, int Size, int RowNum) {
    MPI_Barrier(MPI_COMM_WORLD);
    if (ProcRank == 0) {
        //printf("Initial adjacency matrix:\n");
        //PrintMatrix(pMatrix, Size, Size);
    }
    MPI_Barrier(MPI_COMM_WORLD);
    //ParallelPrintMatrix(pProcRows, Size, RowNum);
}

// Тестування результату паралельного алгоритму Флойда
void TestResult(int* pMatrix, int* pSerialMatrix, int Size) {
    MPI_Barrier(MPI_COMM_WORLD);
    if (ProcRank == 0) {
        SerialFloyd(pSerialMatrix, Size);
        if (!CompareMatrices(pMatrix, pSerialMatrix, Size)) {
            printf("Results of serial and parallel algorithms are NOT identical. Check your code\n");
        } else {
            printf("Results of serial and parallel algorithms are identical\n");
        }
    }
}//
// Created by Matvii Liashenko on 01.12.2025.
//
