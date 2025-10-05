// src/parallel/main.cpp
// Exercise 4 — Task 10: test the parallel program correctness (C++17 + MPI)

#include <iostream>
#include <cmath>
#include <mpi.h>

const double EPS = 1e-6;

// === Initialization ===
void ProcessInitialization(double*& pMatrix, double*& pVector,
                           double*& pResult, int& Size,
                           int ProcRank, int ProcNum) {
    if (ProcRank == 0) {
        do {
            printf("\nEnter size of the matrix and vector: ");
            scanf("%d", &Size);
            if (Size < ProcNum)
                printf("Size must be greater than number of processes!\n");
            if (Size % ProcNum != 0)
                printf("Size must be divisible by number of processes!\n");
        } while ((Size < ProcNum) || (Size % ProcNum != 0));
    }

    MPI_Bcast(&Size, 1, MPI_INT, 0, MPI_COMM_WORLD);

    if (ProcRank == 0) {
        pMatrix = new double[Size * Size];
        pVector = new double[Size];
        pResult = new double[Size];

        for (int i = 0; i < Size; i++) {
            for (int j = 0; j < Size; j++)
                pMatrix[i * Size + j] = i + j + 1;
            pVector[i] = 1.0;
        }

        printf("Initial data generated successfully on process 0.\n");
    } else {
        pVector = new double[Size];
        pResult = nullptr;
    }
}

// === Data distribution ===
void DataDistribution(double* pMatrix, double* pVector,
                      double*& pProcRows, int Size,
                      int ProcRank, int ProcNum) {
    int RowNum = Size / ProcNum;
    pProcRows = new double[RowNum * Size];

    MPI_Bcast(pVector, Size, MPI_DOUBLE, 0, MPI_COMM_WORLD);
    MPI_Scatter(pMatrix, RowNum * Size, MPI_DOUBLE,
                pProcRows, RowNum * Size, MPI_DOUBLE,
                0, MPI_COMM_WORLD);
}

// === Parallel matrix-vector multiplication ===
void ParallelCalculation(double* pProcRows, double* pVector,
                         double*& pProcResult, int Size,
                         int ProcRank, int ProcNum) {
    int RowNum = Size / ProcNum;
    pProcResult = new double[RowNum];

    for (int i = 0; i < RowNum; i++) {
        pProcResult[i] = 0.0;
        for (int j = 0; j < Size; j++)
            pProcResult[i] += pProcRows[i * Size + j] * pVector[j];
    }

    printf("\nProcRank = %d\n", ProcRank);
    printf("Part of result vector:\n");
    for (int i = 0; i < RowNum; i++)
        printf("%8.4f ", pProcResult[i]);
    printf("\n");
}

// === Gather results ===
void ResultGathering(double* pProcResult, double* pResult,
                     int Size, int ProcRank, int ProcNum) {
    int RowNum = Size / ProcNum;

    MPI_Gather(pProcResult, RowNum, MPI_DOUBLE,
               pResult, RowNum, MPI_DOUBLE,
               0, MPI_COMM_WORLD);
}

// === Serial reference computation (only for rank 0) ===
void SerialMultiplication(double* pMatrix, double* pVector,
                          double* pSerialResult, int Size) {
    for (int i = 0; i < Size; i++) {
        pSerialResult[i] = 0.0;
        for (int j = 0; j < Size; j++)
            pSerialResult[i] += pMatrix[i * Size + j] * pVector[j];
    }
}

// === Compare serial and parallel results ===
void TestCorrectness(double* pResult, double* pSerialResult,
                     int Size, int ProcRank) {
    if (ProcRank != 0) return;

    bool correct = true;
    for (int i = 0; i < Size; i++) {
        if (fabs(pResult[i] - pSerialResult[i]) > EPS) {
            printf("Difference detected at index %d: parallel = %.6f, serial = %.6f\n",
                   i, pResult[i], pSerialResult[i]);
            correct = false;
        }
    }

    if (correct)
        printf("\n=== Parallel result matches serial computation ===\n");
    else
        printf("\n*** Parallel result differs from serial computation ***\n");
}

// === Termination ===
void ProcessTermination(double*& pMatrix, double*& pVector,
                        double*& pResult, double*& pProcRows,
                        double*& pProcResult, int ProcRank) {
    if (ProcRank == 0) {
        delete[] pMatrix;
        delete[] pResult;
    }
    delete[] pVector;
    delete[] pProcRows;
    delete[] pProcResult;

    printf("Process %d freed memory.\n", ProcRank);
}

// === Main ===
int main(int argc, char* argv[]) {
    int ProcNum, ProcRank, Size;
    double *pMatrix, *pVector, *pResult, *pProcRows, *pProcResult;
    double* pSerialResult = nullptr;

    MPI_Init(&argc, &argv);
    MPI_Comm_size(MPI_COMM_WORLD, &ProcNum);
    MPI_Comm_rank(MPI_COMM_WORLD, &ProcRank);

    if (ProcRank == 0)
        printf("Parallel matrix-vector multiplication program\n");

    ProcessInitialization(pMatrix, pVector, pResult, Size, ProcRank, ProcNum);
    DataDistribution(pMatrix, pVector, pProcRows, Size, ProcRank, ProcNum);
    ParallelCalculation(pProcRows, pVector, pProcResult, Size, ProcRank, ProcNum);
    ResultGathering(pProcResult, pResult, Size, ProcRank, ProcNum);

    // === NEW: print gathered result on process 0 ===
    if (ProcRank == 0) {
        printf("\nFull result vector gathered on process 0:\n");
        for (int i = 0; i < Size; i++)
            printf("%8.4f ", pResult[i]);
        printf("\n");

        // === Serial check ===
        pSerialResult = new double[Size];
        SerialMultiplication(pMatrix, pVector, pSerialResult, Size);
        TestCorrectness(pResult, pSerialResult, Size, ProcRank);
        delete[] pSerialResult;
    }

    ProcessTermination(pMatrix, pVector, pResult, pProcRows, pProcResult, ProcRank);

    MPI_Finalize();
    return 0;
}

