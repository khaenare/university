#include <iostream>
#include <mpi.h>

int main(int argc, char* argv[]) {
    int ProcNum;    // Number of available processes
    int ProcRank;   // Rank of current process
    double* pMatrix;  // First argument - initial matrix
    double* pVector;  // Second argument - initial vector
    double* pResult;  // Result vector for matrix-vector multiplication
    int Size;         // Sizes of initial matrix and vector
    double Start, Finish, Duration; // timing variables

    // === Initialize MPI environment ===
    MPI_Init(&argc, &argv);

    // === Determine number of processes and rank ===
    MPI_Comm_rank(MPI_COMM_WORLD, &ProcRank);
    MPI_Comm_size(MPI_COMM_WORLD, &ProcNum);

    // === Output process info ===
    std::cout << "Process " << ProcRank << " of " << ProcNum
              << " is active in ParallelMatrixVectorMult." << std::endl;

    // === Finalize MPI ===
    MPI_Finalize();

    return 0;
}
