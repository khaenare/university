cmake_minimum_required(VERSION 3.10)
project(Lab01_MatrixVectorMultiplication LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# === Serial version ===
add_executable(serial_mv
        src/serial/main.cpp
)

# === MPI (parallel) version ===
find_package(MPI REQUIRED)
include_directories(${MPI_INCLUDE_PATH})

add_executable(mpi_mv
        src/mpi/main.cpp
)

target_link_libraries(mpi_mv PRIVATE MPI::MPI_CXX)
