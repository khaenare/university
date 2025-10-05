// src/parallel/main.cpp
// Exercise 4 — Task 6: terminate the calculations (C++17 + MPI)

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
    }
}

// === Function for terminating program and freeing memory ===
void ProcessTermination(double*& pMatrix, double*& pVector,
                        double*& pResult, int ProcRank) {
    if (ProcRank == 0) {
        delete[] pMatrix;
        delete[] pVector;
        delete[] pResult;

        printf("Memory successfully freed on process 0.\n");
    }
}

int main(int argc, char* argv[]) {
    int ProcNum;     // Number of available processes
    int ProcRank;    // Rank of current process
    double* pMatrix; // Initial matrix
    double* pVector; // Initial vector
    double* pResult; // Result vector
    int Size;        // Size of matrix and vector
    double Start, Finish, Duration;

    // === Initialize MPI environment ===
    MPI_Init(&argc, &argv);
    MPI_Comm_size(MPI_COMM_WORLD, &ProcNum);
    MPI_Comm_rank(MPI_COMM_WORLD, &ProcRank);

    if (ProcRank == 0)
        printf("Parallel matrix-vector multiplication program\n");

    // === Memory allocation and data initialization ===
    ProcessInitialization(pMatrix, pVector, pResult, Size, ProcRank, ProcNum);

    printf("Process %d ready (Size = %d)\n", ProcRank, Size);

    // === Task 6: terminate calculations ===
    ProcessTermination(pMatrix, pVector, pResult, ProcRank);

    printf("Process %d finished successfully.\n", ProcRank);

    // === Finalize MPI ===
    MPI_Finalize();

    return 0;
}
