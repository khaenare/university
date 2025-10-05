// src/parallel/main.cpp
// Exercise 4 — Task 7: distribute the data among the processes (C++17 + MPI)

#include <iostream>
#include <mpi.h>

// === Function for memory allocation and data initialization ===
void ProcessInitialization(double*& pMatrix, double*& pVector,
                           double*& pResult, int& Size,
                           int ProcRank, int ProcNum) {
    if (ProcRank == 0) {
        do {
            printf("\nEnter size of the matrix and vector: ");
            scanf("%d", &Size);
            if (Size < ProcNum) {
                printf("Size of the objects must be greater than number of processes!\n");
            }
            if (Size % ProcNum != 0) {
                printf("Size of objects must be divisible by number of processes!\n");
            }
        } while ((Size < ProcNum) || (Size % ProcNum != 0));
    }

    MPI_Bcast(&Size, 1, MPI_INT, 0, MPI_COMM_WORLD);

    if (ProcRank == 0) {
        pMatrix = new double[Size * Size];
        pVector = new double[Size];
        pResult = new double[Size];

        for (int i = 0; i < Size; i++) {
            for (int j = 0; j < Size; j++) {
                pMatrix[i * Size + j] = i + j + 1;
            }
            pVector[i] = 1.0;
        }

        printf("Initial data generated successfully on process 0.\n");
    } else {
        // выделяем память под локальные данные
        pVector = new double[Size];
    }
}

// === Task 7: distribute data among processes ===
void DataDistribution(double* pMatrix, double* pVector,
                      double*& pProcRows, int Size,
                      int ProcRank, int ProcNum) {
    int RowNum = Size / ProcNum; // number of rows per process

    // Выделяем место под часть матрицы
    pProcRows = new double[RowNum * Size];

    // Рассылаем вектор всем процессам
    MPI_Bcast(pVector, Size, MPI_DOUBLE, 0, MPI_COMM_WORLD);

    // Рассылаем части матрицы построчно
    MPI_Scatter(pMatrix, RowNum * Size, MPI_DOUBLE,
                pProcRows, RowNum * Size, MPI_DOUBLE,
                0, MPI_COMM_WORLD);

    printf("Process %d received its part of the matrix (%d rows) and full vector.\n",
           ProcRank, RowNum);
}

// === Function for terminating program and freeing memory ===
void ProcessTermination(double*& pMatrix, double*& pVector,
                        double*& pResult, double*& pProcRows,
                        int ProcRank) {
    if (ProcRank == 0) {
        delete[] pMatrix;
        delete[] pResult;
    }
    delete[] pVector;
    delete[] pProcRows;

    printf("Process %d freed memory.\n", ProcRank);
}

int main(int argc, char* argv[]) {
    int ProcNum;
    int ProcRank;
    double* pMatrix;
    double* pVector;
    double* pResult;
    double* pProcRows;
    int Size;
    double Start, Finish, Duration;

    MPI_Init(&argc, &argv);
    MPI_Comm_size(MPI_COMM_WORLD, &ProcNum);
    MPI_Comm_rank(MPI_COMM_WORLD, &ProcRank);

    if (ProcRank == 0)
        printf("Parallel matrix-vector multiplication program\n");

    ProcessInitialization(pMatrix, pVector, pResult, Size, ProcRank, ProcNum);

    // === Task 7: distribute data ===
    DataDistribution(pMatrix, pVector, pProcRows, Size, ProcRank, ProcNum);

    ProcessTermination(pMatrix, pVector, pResult, pProcRows, ProcRank);

    MPI_Finalize();
    return 0;
}
