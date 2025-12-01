#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>
#include <mpi.h>
// mpic++ /Users/matvii/University/semester_5/ROS-OB/Lab_2/ParallelMM.cpp -o ParallelMM
// mpiexec -n 4 ./ParallelMM

int ProcNum = 0; // Кількість доступних процесів
int ProcRank = 0; // Ранг поточного процесу
int GridSize;         // Розмір віртуальної процесорної решітки
int GridCoords[2];    // Координати поточного процесора в решітці
MPI_Comm GridComm;    // Комунікатор решітки
MPI_Comm ColComm;     // Комунікатор стовпців
MPI_Comm RowComm;     // Комунікатор рядків

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

// Функція для форматованого виводу матриці
void PrintMatrix(double* pMatrix, int RowCount, int ColCount) {
    int i, j; // Змінні циклу
    for (i = 0; i < RowCount; i++) {
        for (j = 0; j < ColCount; j++)
            printf("%7.4f ", pMatrix[i * ColCount + j]);
        printf("\n");
    }
}

// Функція для множення матриць (послідовна версія для блоків)
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

// Функція для множення блоків
void BlockMultiplication(double* pAblock, double* pBblock, double* pCblock, int Size) {
    SerialResultCalculation(pAblock, pBblock, pCblock, Size);
}

// Функція для створення двовимірного комунікатора решітки
// та комунікаторів для кожного рядка і кожного стовпця решітки
void CreateGridCommunicators() {
    int DimSize[2];  // Кількість процесів у кожному вимірі решітки
    int Periodic[2]; // =1, якщо вимір решітки має бути періодичним
    int Subdims[2];  // =1, якщо вимір має належати підрешітці

    DimSize[0] = GridSize;
    DimSize[1] = GridSize;
    Periodic[0] = 0;
    Periodic[1] = 0;

    // Створення декартового комунікатора
    MPI_Cart_create(MPI_COMM_WORLD, 2, DimSize, Periodic, 1, &GridComm);

    // Визначення декартових координат для кожного процесу
    MPI_Cart_coords(GridComm, ProcRank, 2, GridCoords);

    // Створення комунікаторів для рядків
    Subdims[0] = 0; // Фіксація виміру
    Subdims[1] = 1; // Наявність даного виміру в підрешітці
    MPI_Cart_sub(GridComm, Subdims, &RowComm);

    // Створення комунікаторів для стовпців
    Subdims[0] = 1;
    Subdims[1] = 0;
    MPI_Cart_sub(GridComm, Subdims, &ColComm);
}

// Функція для виділення пам'яті та ініціалізації даних
void ProcessInitialization(double* &pAMatrix, double* &pBMatrix, double* &pCMatrix,
    double* &pAblock, double* &pBblock, double* &pCblock,
    double* &pMatrixAblock, int &Size, int &BlockSize) {
    if (ProcRank == 0) {
        do {
            printf("\nEnter the size of matrices: ");
            fflush(stdout);
            fflush(stdout);
            scanf("%d", &Size);
            if (Size % GridSize != 0) {
                printf("Size of matrices must be divisible by the grid size!\n");
            }
        } while (Size % GridSize != 0);
    }
    MPI_Bcast(&Size, 1, MPI_INT, 0, MPI_COMM_WORLD);

    BlockSize = Size / GridSize;
    pAblock = new double[BlockSize * BlockSize];
    pBblock = new double[BlockSize * BlockSize];
    pCblock = new double[BlockSize * BlockSize];
    pMatrixAblock = new double[BlockSize * BlockSize];

    for (int i = 0; i < BlockSize * BlockSize; i++) {
        pCblock[i] = 0;
    }

    if (ProcRank == 0) {
        pAMatrix = new double[Size * Size];
        pBMatrix = new double[Size * Size];
        pCMatrix = new double[Size * Size];
        //DummyDataInitialization(pAMatrix, pBMatrix, Size);
        RandomDataInitialization(pAMatrix, pBMatrix, Size);
    }
}

// Функція для шахового розбиття матриці
void CheckerboardMatrixScatter(double* pMatrix, double* pMatrixBlock, int Size, int BlockSize) {
    double* MatrixRow = new double[BlockSize * Size];
    if (GridCoords[1] == 0) {
        MPI_Scatter(pMatrix, BlockSize * Size, MPI_DOUBLE, MatrixRow,
            BlockSize * Size, MPI_DOUBLE, 0, ColComm);
    }
    for (int i = 0; i < BlockSize; i++) {
        MPI_Scatter(&MatrixRow[i * Size], BlockSize, MPI_DOUBLE,
            &(pMatrixBlock[i * BlockSize]), BlockSize, MPI_DOUBLE, 0, RowComm);
    }
    delete[] MatrixRow;
}

// Розподіл даних між процесами
void DataDistribution(double* pAMatrix, double* pBMatrix, double* pMatrixAblock, double* pBblock, int Size, int BlockSize) {
    // Розподіл матриці між процесами першого стовпця решітки
    CheckerboardMatrixScatter(pAMatrix, pMatrixAblock, Size, BlockSize);
    CheckerboardMatrixScatter(pBMatrix, pBblock, Size, BlockSize);
}

// Функція для збору результуючої матриці
void ResultCollection(double* pCMatrix, double* pCblock, int Size, int BlockSize) {
    double* pResultRow = new double[Size * BlockSize];
    for (int i = 0; i < BlockSize; i++) {
        MPI_Gather(&pCblock[i * BlockSize], BlockSize, MPI_DOUBLE,
            &pResultRow[i * Size], BlockSize, MPI_DOUBLE, 0, RowComm);
    }
    if (GridCoords[1] == 0) {
        MPI_Gather(pResultRow, BlockSize * Size, MPI_DOUBLE, pCMatrix,
            BlockSize * Size, MPI_DOUBLE, 0, ColComm);
    }
    delete[] pResultRow;
}

// Розсилка блоків матриці A по рядках процесорної решітки
void ABlockCommunication(int iter, double* pAblock, double* pMatrixAblock, int BlockSize) {
    // Визначення ведучого процесу рядка процесорної решітки
    int Pivot = (GridCoords[0] + iter) % GridSize;

    // Копіювання блоку, що пересилається, в окремий буфер пам'яті
    if (GridCoords[1] == Pivot) {
        for (int i = 0; i < BlockSize * BlockSize; i++)
            pAblock[i] = pMatrixAblock[i];
    }

    // Розсилка блоку
    MPI_Bcast(pAblock, BlockSize * BlockSize, MPI_DOUBLE, Pivot, RowComm);
}

// Функція для циклічного зсуву блоків матриці B
void BblockCommunication(double* pBblock, int BlockSize) {
    MPI_Status Status;
    int NextProc = GridCoords[0] + 1;
    if (GridCoords[0] == GridSize - 1) NextProc = 0;
    int PrevProc = GridCoords[0] - 1;
    if (GridCoords[0] == 0) PrevProc = GridSize - 1;

    MPI_Sendrecv_replace(pBblock, BlockSize * BlockSize, MPI_DOUBLE,
        NextProc, 0, PrevProc, 0, ColComm, &Status);
}

// Функція для паралельного виконання методу Фокса
void ParallelResultCalculation(double* pAblock, double* pMatrixAblock,
    double* pBblock, double* pCblock, int BlockSize) {
    for (int iter = 0; iter < GridSize; iter++) {
        // Розсилка блоків матриці A по рядках процесорної решітки
        ABlockCommunication(iter, pAblock, pMatrixAblock, BlockSize);
        // Множення блоків
        BlockMultiplication(pAblock, pBblock, pCblock, BlockSize);
        // Циклічний зсув блоків матриці B у стовпцях процесорної решітки
        BblockCommunication(pBblock, BlockSize);
    }
}

// Тестовий вивід блоку матриці
void TestBlocks(double* pBlock, int BlockSize, char str[]) {
    MPI_Barrier(MPI_COMM_WORLD);
    if (ProcRank == 0) {
        printf("%s \n", str);
    }
    for (int i = 0; i < ProcNum; i++) {
        if (ProcRank == i) {
            printf("ProcRank = %d \n", ProcRank);
            PrintMatrix(pBlock, BlockSize, BlockSize);
        }
        MPI_Barrier(MPI_COMM_WORLD);
    }
}

// Функція для перевірки результату множення матриць
void TestResult(double* pAMatrix, double* pBMatrix, double* pCMatrix, int Size) {
    double* pSerialResult;
    double Accuracy = 1.e-6;
    int equal = 0;
    int i;
    if (ProcRank == 0) {
        pSerialResult = new double[Size * Size];
        for (i = 0; i < Size * Size; i++) {
            pSerialResult[i] = 0;
        }
        SerialResultCalculation(pAMatrix, pBMatrix, pSerialResult, Size);
        for (i = 0; i < Size * Size; i++) {
            if (fabs(pSerialResult[i] - pCMatrix[i]) >= Accuracy)
                equal = 1;
        }
        if (equal == 1)
            printf("The results of serial and parallel algorithms are NOT identical. Check your code.\n");
        else
            printf("The results of serial and parallel algorithms are identical.\n");
        delete[] pSerialResult;
    }
}

// Функція для завершення обчислювального процесу
void ProcessTermination(double* pAMatrix, double* pBMatrix, double* pCMatrix,
    double* pAblock, double* pBblock, double* pCblock, double* pMatrixAblock) {
    if (ProcRank == 0) {
        delete[] pAMatrix;
        delete[] pBMatrix;
        delete[] pCMatrix;
    }
    delete[] pAblock;
    delete[] pBblock;
    delete[] pCblock;
    delete[] pMatrixAblock;
}

int main(int argc, char* argv[]) {
    double* pAMatrix; // Перший аргумент множення матриць
    double* pBMatrix; // Другий аргумент множення матриць
    double* pCMatrix; // Результуюча матриця
    int Size;         // Розмір матриць
    int BlockSize;    // Розміри блоків матриці
    double* pAblock;       // Поточний блок матриці A
    double* pBblock;       // Поточний блок матриці B
    double* pCblock;       // Блок результуючої матриці C
    double* pMatrixAblock; // Початковий блок матриці A
    double Start, Finish, Duration;

    setvbuf(stdout, 0, _IONBF, 0);
    MPI_Init(&argc, &argv);
    MPI_Comm_size(MPI_COMM_WORLD, &ProcNum);
    MPI_Comm_rank(MPI_COMM_WORLD, &ProcRank);

    GridSize = sqrt((double)ProcNum);
    if (ProcNum != GridSize * GridSize) {
        if (ProcRank == 0) {
            printf("Number of processes must be a perfect square \n");
        }
    }
    else {
        if (ProcRank == 0)
            printf("Parallel matrix multiplication program\n");

        // Створення декартової решітки, комунікаторів рядків і стовпців
        CreateGridCommunicators();

        // Виділення пам'яті та ініціалізація елементів матриці
        ProcessInitialization(pAMatrix, pBMatrix, pCMatrix, pAblock, pBblock,
            pCblock, pMatrixAblock, Size, BlockSize);

        DataDistribution(pAMatrix, pBMatrix, pMatrixAblock, pBblock, Size, BlockSize);

        // Виконання методу Фокса
        Start = MPI_Wtime();
        ParallelResultCalculation(pAblock, pMatrixAblock, pBblock, pCblock, BlockSize);
        ResultCollection(pCMatrix, pCblock, Size, BlockSize);
        Finish = MPI_Wtime();
        Duration = Finish - Start;

        TestResult(pAMatrix, pBMatrix, pCMatrix, Size);

        if (ProcRank == 0) {
            printf("Time of execution = %f\n", Duration);
        }

        // Завершення процесу
        ProcessTermination(pAMatrix, pBMatrix, pCMatrix, pAblock, pBblock,
            pCblock, pMatrixAblock);
    }

    MPI_Finalize();
    return 0;
}