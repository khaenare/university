#include <iostream>
#include <cmath>
#include <mpi.h>

const double EPS = 1e-6;

// === Initialization ===
void ProcessInitialization(double*& pMatrix, double*& pVector,
                           double*& pResult, int& Size,
                           int ProcRank, int ProcNum) {
    if (ProcRank == 0) {
        printf("\nEnter size of the matrix and vector: ");
        scanf("%d", &Size);
        if (Size < ProcNum)
            printf("Warning: number of processes exceeds matrix size.\n");
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

// === Flexible data distribution ===
void DataDistribution(double* pMatrix, double* pVector,
                      double*& pProcRows, int Size,
                      int ProcRank, int ProcNum,
                      int*& sendcounts, int*& displs,
                      int& RowNum) {
    // compute rows per process (some will have one more)
    int base = Size / ProcNum;
    int extra = Size % ProcNum;

    sendcounts = new int[ProcNum];
    displs = new int[ProcNum];
    displs[0] = 0;

    for (int i = 0; i < ProcNum; i++) {
        int rows = (i < extra) ? base + 1 : base;
        sendcounts[i] = rows * Size;
        if (i > 0)
            displs[i] = displs[i - 1] + sendcounts[i - 1];
    }

    RowNum = (ProcRank < extra) ? base + 1 : base;
    pProcRows = new double[RowNum * Size];

    MPI_Bcast(pVector, Size, MPI_DOUBLE, 0, MPI_COMM_WORLD);
    MPI_Scatterv(pMatrix, sendcounts, displs, MPI_DOUBLE,
                 pProcRows, RowNum * Size, MPI_DOUBLE,
                 0, MPI_COMM_WORLD);
}

// === Parallel computation ===
void ParallelCalculation(double* pProcRows, double* pVector,
                         double*& pProcResult, int Size,
                         int RowNum, int ProcRank) {
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

// === Gather results flexibly ===
void ResultGathering(double* pProcResult, double* pResult,
                     int Size, int ProcRank, int ProcNum,
                     int* sendcounts, int* displs, int RowNum) {
    int* recvcounts = nullptr;
    int* recvdispls = nullptr;

    if (ProcRank == 0) {
        recvcounts = new int[ProcNum];
        recvdispls = new int[ProcNum];
        recvcounts[0] = sendcounts[0] / Size;
        recvdispls[0] = 0;
        for (int i = 1; i < ProcNum; i++) {
            recvcounts[i] = sendcounts[i] / Size;
            recvdispls[i] = recvdispls[i - 1] + recvcounts[i - 1];
        }
    }

    MPI_Gatherv(pProcResult, RowNum, MPI_DOUBLE,
                pResult, recvcounts, recvdispls, MPI_DOUBLE,
                0, MPI_COMM_WORLD);

    if (ProcRank == 0) {
        printf("\nFull result vector gathered on process 0:\n");
        for (int i = 0; i < Size; i++)
            printf("%8.4f ", pResult[i]);
        printf("\n");

        delete[] recvcounts;
        delete[] recvdispls;
    }
}

// === Serial computation for check ===
void SerialMultiplication(double* pMatrix, double* pVector,
                          double* pSerialResult, int Size) {
    for (int i = 0; i < Size; i++) {
        pSerialResult[i] = 0.0;
        for (int j = 0; j < Size; j++)
            pSerialResult[i] += pMatrix[i * Size + j] * pVector[j];
    }
}

void TestCorrectness(double* pResult, double* pSerialResult,
                     int Size, int ProcRank) {
    if (ProcRank != 0) return;

    bool correct = true;
    for (int i = 0; i < Size; i++) {
        if (fabs(pResult[i] - pSerialResult[i]) > EPS) {
            printf("Mismatch at index %d: parallel = %.6f, serial = %.6f\n",
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
                        double*& pProcResult, int*& sendcounts,
                        int*& displs, int ProcRank) {
    if (ProcRank == 0) {
        delete[] pMatrix;
        delete[] pResult;
    }
    delete[] pVector;
    delete[] pProcRows;
    delete[] pProcResult;
    delete[] sendcounts;
    delete[] displs;

    printf("Process %d freed memory.\n", ProcRank);
}

// === Main ===
int main(int argc, char* argv[]) {
    int ProcNum, ProcRank, Size;
    double *pMatrix, *pVector, *pResult, *pProcRows, *pProcResult;
    double* pSerialResult = nullptr;
    int *sendcounts = nullptr, *displs = nullptr;
    int RowNum = 0;

    MPI_Init(&argc, &argv);
    MPI_Comm_size(MPI_COMM_WORLD, &ProcNum);
    MPI_Comm_rank(MPI_COMM_WORLD, &ProcRank);

    if (ProcRank == 0)
        printf("Parallel matrix-vector multiplication program\n");

    ProcessInitialization(pMatrix, pVector, pResult, Size, ProcRank, ProcNum);
    DataDistribution(pMatrix, pVector, pProcRows, Size, ProcRank, ProcNum,
                     sendcounts, displs, RowNum);
    ParallelCalculation(pProcRows, pVector, pProcResult, Size, RowNum, ProcRank);
    ResultGathering(pProcResult, pResult, Size, ProcRank, ProcNum,
                    sendcounts, displs, RowNum);

    if (ProcRank == 0) {
        pSerialResult = new double[Size];
        SerialMultiplication(pMatrix, pVector, pSerialResult, Size);
        TestCorrectness(pResult, pSerialResult, Size, ProcRank);
        delete[] pSerialResult;
    }

    ProcessTermination(pMatrix, pVector, pResult, pProcRows,
                       pProcResult, sendcounts, displs, ProcRank);

    MPI_Finalize();
    return 0;
}
