#include <iostream>
#include <mpi.h>

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

// === Task 9: gather results on process 0 ===
void ResultGathering(double* pProcResult, double* pResult,
                     int Size, int ProcRank, int ProcNum) {
    int RowNum = Size / ProcNum;

    MPI_Gather(pProcResult, RowNum, MPI_DOUBLE,
               pResult, RowNum, MPI_DOUBLE,
               0, MPI_COMM_WORLD);

    if (ProcRank == 0) {
        printf("\nFull result vector gathered on process 0:\n");
        for (int i = 0; i < Size; i++)
            printf("%8.4f ", pResult[i]);
        printf("\n");
    }
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

    MPI_Init(&argc, &argv);
    MPI_Comm_size(MPI_COMM_WORLD, &ProcNum);
    MPI_Comm_rank(MPI_COMM_WORLD, &ProcRank);

    if (ProcRank == 0)
        printf("Parallel matrix-vector multiplication program\n");

    ProcessInitialization(pMatrix, pVector, pResult, Size, ProcRank, ProcNum);
    DataDistribution(pMatrix, pVector, pProcRows, Size, ProcRank, ProcNum);
    ParallelCalculation(pProcRows, pVector, pProcResult, Size, ProcRank, ProcNum);
    ResultGathering(pProcResult, pResult, Size, ProcRank, ProcNum);
    ProcessTermination(pMatrix, pVector, pResult, pProcRows, pProcResult, ProcRank);

    MPI_Finalize();
    return 0;
}
