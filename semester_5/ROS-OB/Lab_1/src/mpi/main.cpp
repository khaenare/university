#include <iostream>
#include <mpi.h>

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

    // === Output information (strictly per lab manual) ===
    printf("Parallel matrix-vector multiplication program\n");
    printf("Number of available processes = %d\n", ProcNum);
    printf("Rank of current process = %d\n", ProcRank);

    // === Finalize MPI ===
    MPI_Finalize();

    return 0;
}
