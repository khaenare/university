#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>
#include <mpi.h>
#include <algorithm> // Для std::copy
#include <locale.h>  // Для коректної обробки крапки
#include <unistd.h>  // Для usleep

static int ProcNum = 0;      // Кількість доступних процесів
static int ProcRank = -1;    // Ранг поточного процесу

// Функція для розподілу рядків сітки між процесами
void DataDistribution(double* pMatrix, double* pProcRows, int RowNum, int Size) {
    int* pSendNum = new int[ProcNum];
    int* pSendInd = new int[ProcNum];

    int currentRestRows = Size; // Поточна кількість рядків для розподілу

    // Розраховуємо кількість рядків для кожного процесу за тією ж формулою, що і при ініціалізації
    pSendInd[0] = 0;
    for (int i = 0; i < ProcNum; i++) {
        int rowNumForProcess = (currentRestRows - 2) / (ProcNum - i) + 2;
        pSendNum[i] = rowNumForProcess * Size;

        if (i > 0) {
            // Зсув = попередній зсув + розмір попереднього блоку - перекриття (Size)
            pSendInd[i] = pSendInd[i-1] + pSendNum[i-1] - Size;
        }

        // Оновлюємо залишок рядків (формула з методички: RestRows - RestRows / (Procs - i))
        currentRestRows = currentRestRows - currentRestRows / (ProcNum - i);
    }

    MPI_Scatterv(pMatrix, pSendNum, pSendInd, MPI_DOUBLE, pProcRows,
        pSendNum[ProcRank], MPI_DOUBLE, 0, MPI_COMM_WORLD);

    delete[] pSendInd;
    delete[] pSendNum;
}

// Функція для завершення обчислювального процесу
void ProcessTermination(double* pMatrix, double* pProcRows) {
    if (pMatrix != NULL) delete[] pMatrix;
    if (pProcRows != NULL) delete[] pProcRows;
}

// Функція для виконання ітерації методу Гаусса-Зейделя
double IterationCalculation(double* pProcRows, int Size, int RowNum) {
    int i, j;
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

// Функція для простої ініціалізації значень вузлів сітки
void DummyDataInitialization(double* pMatrix, int Size) {
    int i, j;
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
    int RestRows;

    if (ProcRank == 0) {
        do {
            printf("\nEnter the grid size: ");
            fflush(stdout);
            scanf("%d", &Size);

            if (Size <= 2) printf("\n Size of grid must be greater than 2! \n");
            if (Size < ProcNum) printf("Size of grid must be greater than the number of processes! \n");
        } while ((Size <= 2) || (Size < ProcNum));

        do {
            printf("\nEnter the required accuracy: ");
            fflush(stdout);
            scanf("%lf", &Eps);

            printf("\nChosen accuracy = %lf", Eps);
            if (Eps <= 0) printf("\nAccuracy must be greater than 0!\n");
        } while (Eps <= 0);
    }

    MPI_Bcast(&Size, 1, MPI_INT, 0, MPI_COMM_WORLD);
    MPI_Bcast(&Eps, 1, MPI_DOUBLE, 0, MPI_COMM_WORLD);

    RestRows = Size;
    for (int i = 0; i < ProcRank; i++)
        RestRows = RestRows - RestRows / (ProcNum - i);
    RowNum = (RestRows - 2) / (ProcNum - ProcRank) + 2;

    pProcRows = new double[RowNum * Size];

    // Виділяємо пам'ять із запасом, щоб уникнути помилок доступу на великих матрицях
    pMatrix = new double[Size * (Size + ProcNum)];

    if (ProcRank == 0) {
        DummyDataInitialization(pMatrix, Size);
    } else {
        // Очистка пам'яті
        for(int k=0; k < Size * Size; k++) pMatrix[k] = 0.0;
    }
}

// Функція для обміну граничними рядками смуг процесів
void ExchangeData(double* pProcRows, int Size, int RowNum) {
    MPI_Status status;
    int NextProcNum = (ProcRank == ProcNum - 1) ? MPI_PROC_NULL : ProcRank + 1;
    int PrevProcNum = (ProcRank == 0) ? MPI_PROC_NULL : ProcRank - 1;

    MPI_Sendrecv(pProcRows + Size * (RowNum - 2), Size, MPI_DOUBLE,
        NextProcNum, 4, pProcRows, Size, MPI_DOUBLE, PrevProcNum, 4,
        MPI_COMM_WORLD, &status);

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
        ExchangeData(pProcRows, Size, RowNum);
        ProcDelta = IterationCalculation(pProcRows, Size, RowNum);
        MPI_Allreduce(&ProcDelta, &Delta, 1, MPI_DOUBLE, MPI_MAX, MPI_COMM_WORLD);
    } while (Delta > Eps);
}

// Функція для збору результату вектора
void ResultCollection(double* pMatrix, double* pProcRows, int Size, int RowNum) {
    int* pReceiveNum = new int[ProcNum];
    int* pReceiveInd = new int[ProcNum];

    int currentRestRows = Size;

    // Використовуємо ту саму виправлену логіку для збору даних
    pReceiveInd[0] = 0;
    for (int i = 0; i < ProcNum; i++) {
        int rowNumForProcess = (currentRestRows - 2) / (ProcNum - i) + 2;
        pReceiveNum[i] = rowNumForProcess * Size;

        if (i > 0) {
            pReceiveInd[i] = pReceiveInd[i-1] + pReceiveNum[i-1] - Size;
        }

        currentRestRows = currentRestRows - currentRestRows / (ProcNum - i);
    }

    MPI_Allgatherv(pProcRows, pReceiveNum[ProcRank], MPI_DOUBLE, pMatrix,
        pReceiveNum, pReceiveInd, MPI_DOUBLE, MPI_COMM_WORLD);

    delete[] pReceiveNum;
    delete[] pReceiveInd;
}

void CopyData(double* pMatrix, int Size, double* pSerialMatrix) {
    std::copy(pMatrix, pMatrix + Size * Size, pSerialMatrix);
}

int main(int argc, char* argv[]) {
    setvbuf(stdout, NULL, _IONBF, 0);
    setlocale(LC_NUMERIC, "C");

    double* pMatrix = NULL;
    double* pProcRows = NULL;
    double* pSerialMatrix = NULL;
    int Size;
    int RowNum;
    double Eps;
    int Iterations;
    double Start, Finish, Duration;

    MPI_Init(&argc, &argv);
    MPI_Comm_size(MPI_COMM_WORLD, &ProcNum);
    MPI_Comm_rank(MPI_COMM_WORLD, &ProcRank);

    if (ProcRank == 0) {
        printf("Parallel Gauss Seidel algorithm \n");
    }

    ProcessInitialization(pMatrix, pProcRows, Size, RowNum, Eps);

    // Пауза перед стартом замірів
    MPI_Barrier(MPI_COMM_WORLD);
    Start = MPI_Wtime();

    DataDistribution(pMatrix, pProcRows, RowNum, Size);
    ParallelResultCalculation(pProcRows, Size, RowNum, Eps, Iterations);
    ResultCollection(pMatrix, pProcRows, Size, RowNum);

    MPI_Barrier(MPI_COMM_WORLD);
    Finish = MPI_Wtime();
    Duration = Finish - Start;

    if (ProcRank == 0) {
        printf("\nIter %d \n", Iterations);
        printf("\nExecution time: %f\n", Duration);
    }

    ProcessTermination(pMatrix, pProcRows);

    MPI_Barrier(MPI_COMM_WORLD);
    usleep(100000);
    MPI_Finalize();
    return 0;
}