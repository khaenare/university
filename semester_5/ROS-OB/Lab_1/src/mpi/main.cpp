#include <iostream>
#include <mpi.h>

// Function for memory allocation and data initialization
void ProcessInitialization(double*& pMatrix, double*& pVector,
                           double*& pResult, int& Size,
                           int ProcRank, int ProcNum) {
    if (ProcRank == 0) {
        do {
            printf("\nEnter size of the matrix and vector: ");
            scanf("%d", &Size);
            if (Size < ProcNum) {
                printf("Size of the objects must be greater than "
                       "number of processes!\n");
            }
            if (Size % ProcNum != 0) {
                printf("Size of objects must be divisible by "
                       "number of processes!\n");
            }
        } while ((Size < ProcNum) || (Size % ProcNum != 0));
    }

    MPI_Bcast(&Size, 1, MPI_INT, 0, MPI_COMM_WORLD);
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

    // === Determine number of processes and rank ===
    MPI_Comm_size(MPI_COMM_WORLD, &ProcNum);
    MPI_Comm_rank(MPI_COMM_WORLD, &ProcRank);

    if (ProcRank == 0)
        printf("Parallel matrix-vector multiplication program\n");

    // === Memory allocation and data initialization ===
    // Replace the prints from Task 3 with the initialization call:
    ProcessInitialization(pMatrix, pVector, pResult, Size, ProcRank, ProcNum);

    printf("Process %d received Size = %d\n", ProcRank, Size);

    // === Finalize MPI ===
    MPI_Finalize();

    return 0;
}
