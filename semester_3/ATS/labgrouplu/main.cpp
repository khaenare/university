#include <iostream>
#include <iomanip>
using namespace std;

template<typename T>
T** createMatrix(int size) {
    T** matrix = new T*[size]; 
    for (int index = 0; index < size; ++index) {
        matrix[index] = new T[size]; 
    }
    return matrix;
}

template<typename T>
void deleteMatrix(T** matrix, int size) { 
    for (int index = 0; index < size; ++index) {
        delete[] matrix[index]; 
    }
    delete[] matrix; 
}

template<typename T>
T** computeInverseLU(T** inputMat, int size) {
    T** lower = createMatrix<T>(size);
    T** upper = createMatrix<T>(size);
    T** resultInv = createMatrix<T>(size);

    // Ініціалізація матриці
    for (int row = 0; row < size; ++row) {
        for (int col = 0; col < size; ++col) {
            lower[row][col] = 0;
            upper[row][col] = 0;
            resultInv[row][col] = 0;
        }
    }

    // LU розклад
    for (int diag = 0; diag < size; ++diag) {
        for (int col = diag; col < size; ++col) {
            upper[diag][col] = inputMat[diag][col];
            for (int inner = 0; inner < diag; ++inner) upper[diag][col] -= lower[diag][inner] * upper[inner][col];
        }
        for (int row = diag; row < size; ++row) {
            if (diag == row) lower[diag][diag] = 1;
            else {
                lower[row][diag] = inputMat[row][diag];
                for (int inner = 0; inner < diag; ++inner) lower[row][diag] -= lower[row][inner] * upper[inner][diag];
                lower[row][diag] /= upper[diag][diag];
            }
        }
    }

    // Обернене обчислення з використанням прямої та зворотної підстановки
    T** identity = createMatrix<T>(size);
    for (int i = 0; i < size; ++i) identity[i][i] = 1;

    for (int col = 0; col < size; ++col) {
        T* tempVec = new T[size];
        for (int row = 0; row < size; ++row) {
            tempVec[row] = identity[row][col];
            for (int inner = 0; inner < row; ++inner) tempVec[row] -= lower[row][inner] * tempVec[inner];
        }
        for (int row = size - 1; row >= 0; --row) {
            resultInv[row][col] = tempVec[row];
            for (int inner = row + 1; inner < size; ++inner) resultInv[row][col] -= upper[row][inner] * resultInv[inner][col];
            resultInv[row][col] /= upper[row][row];
        }
        delete[] tempVec;
    }

    deleteMatrix(lower, size);
    deleteMatrix(upper, size);
    deleteMatrix(identity, size);

    return resultInv;
}

int main() {
    int matrixSize;
    cout << "Enter the dimension of the matrix (n x n): ";
    cin >> matrixSize;

    double** matrix = createMatrix<double>(matrixSize);

    cout << "Enter elements of the matrix (size " << matrixSize << " x " << matrixSize << "):\n";
    for (int row = 0; row < matrixSize; ++row) {
        for (int col = 0; col < matrixSize; ++col) {
            cin >> matrix[row][col];
        }
    }

    double** inverseMatrix = computeInverseLU(matrix, matrixSize);

    cout << "\nThe inverse of the matrix is:\n";
    cout << fixed << setprecision(6);
    for (int row = 0; row < matrixSize; ++row) {
        for (int col = 0; col < matrixSize; ++col) {
            cout << inverseMatrix[row][col] << " ";
        }
        cout << endl;
    }

    deleteMatrix(matrix, matrixSize);
    deleteMatrix(inverseMatrix, matrixSize);

    return 0;
}
