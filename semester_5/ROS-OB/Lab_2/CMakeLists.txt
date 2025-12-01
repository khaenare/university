cmake_minimum_required(VERSION 3.20)
project(MatrixLab)

set(CMAKE_CXX_STANDARD 14)

# 1. Находим пакет MPI
find_package(MPI REQUIRED)

# 2. Настройка для Serial (обычный C++)
add_executable(SerialApp SerialMM.cpp)

# 3. Настройка для Parallel (MPI)
add_executable(ParallelApp ParallelMM.cpp)
# Линкуем MPI библиотеки к параллельной программе
target_link_libraries(ParallelApp PUBLIC MPI::MPI_CXX)
