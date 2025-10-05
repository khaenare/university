#include <iostream>
#include <mpi.h>

int main(int argc, char* argv[]) {
    // === Initialize MPI environment ===
    MPI_Init(&argc, &argv);

    std::cout << "MPI environment initialized successfully." << std::endl;

    // === Finalize MPI ===
    MPI_Finalize();

    std::cout << "MPI environment finalized successfully." << std::endl;

    return 0;
}
