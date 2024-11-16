#include <iostream>
#include <iomanip>
using namespace std;

template<typename T>
T** createMatrix(int n) {
    T** matrix = new T*[n];
    for (int i = 0; i < n; ++i) {
        matrix[i] = new T[n];
    }
    return matrix;
}

template<typename T>
void deleteMatrix(T** matrix, int n) {
    for (int i = 0; i < n; ++i) {
        delete[] matrix[i];
    }
    delete[] matrix;
}

template<typename T>
T** inverseLU(T** A, int n) {
    T** L = createMatrix<T>(n);
    T** U = createMatrix<T>(n);
    T** inv = createMatrix<T>(n);

    // Ініціалізація матриці
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            L[i][j] = 0;
            U[i][j] = 0;
            inv[i][j] = 0;
        }
    }

    // LU розклад
    for (int i = 0; i < n; ++i) {
        for (int j = i; j < n; ++j) {
            U[i][j] = A[i][j];
            for (int k = 0; k < i; ++k) U[i][j] -= L[i][k] * U[k][j];
        }
        for (int j = i; j < n; ++j) {
            if (i == j) L[i][i] = 1;
            else {
                L[j][i] = A[j][i];
                for (int k = 0; k < i; ++k) L[j][i] -= L[j][k] * U[k][i];
                L[j][i] /= U[i][i];
            }
        }
    }

    // Обернене обчислення з використанням прямої та зворотної підстановки
    T** I = createMatrix<T>(n);
    for (int i = 0; i < n; ++i) I[i][i] = 1;

    for (int i = 0; i < n; ++i) {
        T* y = new T[n];
        for (int j = 0; j < n; ++j) {
            y[j] = I[j][i];
            for (int k = 0; k < j; ++k) y[j] -= L[j][k] * y[k];
        }
        for (int j = n - 1; j >= 0; --j) {
            inv[j][i] = y[j];
            for (int k = j + 1; k < n; ++k) inv[j][i] -= U[j][k] * inv[k][i];
            inv[j][i] /= U[j][j];
        }
        delete[] y;
    }

    deleteMatrix(L, n);
    deleteMatrix(U, n);
    deleteMatrix(I, n);

    return inv;
}

int main() {
    int n;
    cout << "Enter the size of the matrix (n x n): ";
    cin >> n;

    
    double** A = createMatrix<double>(n);

    cout << "Enter elements of the matrix A (n x n):\n";
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            cin >> A[i][j];
        }
    }

    double** invA = inverseLU(A, n);

    cout << "\nThe inverse of matrix A is:\n";
    cout << fixed << setprecision(6); 
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            cout << invA[i][j] << " "; 
        }
        cout << endl;
    }

    deleteMatrix(A, n);
    deleteMatrix(invA, n);

    return 0;
}
