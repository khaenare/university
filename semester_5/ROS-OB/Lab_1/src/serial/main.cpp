#include <iostream>

int main() {
    double* pMatrix = nullptr;
    double* pVector = nullptr;
    double* pResult = nullptr;
    int Size = 0;

    std::cout << "Serial matrix-vector multiplication program" << std::endl;

    // === Task 2: Input the size of the matrix and vector ===
    do {
        std::cout << "Enter the size of the initial objects: ";
        std::cin >> Size;

        if (std::cin.fail() || Size <= 0) {
            std::cin.clear();
            std::cin.ignore(32767, '\n');
            std::cout << "Error: size must be a positive integer." << std::endl;
            Size = 0;
        }
    } while (Size <= 0);

    std::cout << "Chosen objects size = " << Size << std::endl;

    return 0;
}