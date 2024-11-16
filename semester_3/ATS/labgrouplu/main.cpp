#include <iostream>
#include <iomanip>
#include <stdexcept>
using namespace std;

// Структура для представлення матриці
typedef struct MTX {
    int size; // Розмір матриці
    double** elements; // Двовимірний масив для зберігання елементів матриці

    // Конструктор для створення матриці
    MTX(int size) {
        this->size = size;
        elements = new double*[size];
        for (int i = 0; i < size; i++)
            elements[i] = new double[size]();
    }

    // Деструктор для звільнення пам'яті
    ~MTX() {
        for (int i = 0; i < size; ++i)
            delete[] elements[i];
        delete[] elements;
    }
} MTX;

// Функція для додавання двох матриць
MTX addMatrices(MTX A, MTX B) {
    MTX C(A.size);
    for (int i = 0; i < A.size; i++) {
        for (int j = 0; j < A.size; j++) {
            C.elements[i][j] = A.elements[i][j] + B.elements[i][j];
        }
    }
    return C;
}

// Функція для віднімання двох матриць
MTX subtractMatrices(MTX A, MTX B) {
    MTX C(A.size);
    for (int i = 0; i < A.size; i++) {
        for (int j = 0; j < A.size; j++) {
            C.elements[i][j] = A.elements[i][j] - B.elements[i][j];
        }
    }
    return C;
}

// Функція для розбиття матриці на підматриці
MTX splitMatrix(MTX A, int startRow, int startCol) {
    int halfSize = A.size / 2;
    MTX C(halfSize);
    for (int i = 0; i < halfSize; i++) {
        for (int j = 0; j < halfSize; j++) {
            C.elements[i][j] = A.elements[startRow + i][startCol + j];
        }
    }
    return C;
}

// Функція для заповнення підматриці в матрицю
MTX fillSubMatrix(MTX C, MTX subMatrix, int startRow, int startCol) {
    for (int i = 0; i < subMatrix.size; i++) {
        for (int j = 0; j < subMatrix.size; j++) {
            C.elements[i + startRow][j + startCol] = subMatrix.elements[i][j];
        }
    }
    return C;
}

// Просте множення матриць
MTX simpleMultiply(MTX A, MTX B) {
    MTX C(A.size);
    for (int i = 0; i < A.size; ++i) {
        for (int j = 0; j < A.size; ++j) {
            for (int k = 0; k < A.size; ++k) {
                C.elements[i][j] += A.elements[i][k] * B.elements[k][j];
            }
        }
    }
    return C;
}

// Алгоритм Штрассена для множення матриць
MTX strassenMultiply(MTX A, MTX B) {
    if (A.size == 2) {
        return simpleMultiply(A, B);
    }

    int halfSize = A.size / 2;

    MTX A11 = splitMatrix(A, 0, 0);
    MTX A12 = splitMatrix(A, 0, halfSize);
    MTX A21 = splitMatrix(A, halfSize, 0);
    MTX A22 = splitMatrix(A, halfSize, halfSize);
    MTX B11 = splitMatrix(B, 0, 0);
    MTX B12 = splitMatrix(B, 0, halfSize);
    MTX B21 = splitMatrix(B, halfSize, 0);
    MTX B22 = splitMatrix(B, halfSize, halfSize);

    MTX M1 = strassenMultiply(addMatrices(A11, A22), addMatrices(B11, B22));
    MTX M2 = strassenMultiply(addMatrices(A21, A22), B11);
    MTX M3 = strassenMultiply(A11, subtractMatrices(B12, B22));
    MTX M4 = strassenMultiply(A22, subtractMatrices(B21, B11));
    MTX M5 = strassenMultiply(addMatrices(A11, A12), B22);
    MTX M6 = strassenMultiply(subtractMatrices(A21, A11), addMatrices(B11, B12));
    MTX M7 = strassenMultiply(subtractMatrices(A12, A22), addMatrices(B21, B22));

    MTX C(A.size);
    MTX C11 = subtractMatrices(addMatrices(addMatrices(M1, M4), M7), M5);
    MTX C12 = addMatrices(M3, M5);
    MTX C21 = addMatrices(M2, M4);
    MTX C22 = subtractMatrices(addMatrices(addMatrices(M1, M3), M6), M2);

    C = fillSubMatrix(C, C11, 0, 0);
    C = fillSubMatrix(C, C12, 0, halfSize);
    C = fillSubMatrix(C, C21, halfSize, 0);
    C = fillSubMatrix(C, C22, halfSize, halfSize);

    return C;
}

// Функція для знаходження оберненої матриці за допомогою LU-розкладу
MTX computeInverseLU(MTX inputMatrix) {
    int size = inputMatrix.size;
    MTX lower(size);
    MTX upper(size);
    MTX inverse(size);

    // Ініціалізація
    for (int i = 0; i < size; ++i) {
        for (int j = 0; j < size; ++j) {
            lower.elements[i][j] = (i == j) ? 1 : 0;
            upper.elements[i][j] = 0;
            inverse.elements[i][j] = 0;
        }
    }

    // LU-розклад
    for (int i = 0; i < size; ++i) {
        // Визначення верхньої трикутної матриці U
        for (int j = i; j < size; ++j) {
            upper.elements[i][j] = inputMatrix.elements[i][j];
            for (int k = 0; k < i; ++k) {
                upper.elements[i][j] -= lower.elements[i][k] * upper.elements[k][j];
            }
        }

        // Перевірка на майже нульовий елемент
        if (abs(upper.elements[i][i]) < 1e-9) {
            throw runtime_error("Matrix is nearly singular and cannot be inverted.");
        }

        // Визначення нижньої трикутної матриці L
        for (int j = i + 1; j < size; ++j) {
            lower.elements[j][i] = inputMatrix.elements[j][i];
            for (int k = 0; k < i; ++k) {
                lower.elements[j][i] -= lower.elements[j][k] * upper.elements[k][i];
            }
            lower.elements[j][i] /= upper.elements[i][i];
        }
    }

    // Знаходження оберненої матриці за допомогою прямої та зворотної підстановки
    for (int i = 0; i < size; ++i) {
        MTX identity(size);
        identity.elements[i][i] = 1;

        // Прямий хід для знаходження вектора y (Ly = e)
        MTX y(size);
        for (int j = 0; j < size; ++j) {
            y.elements[j][0] = identity.elements[j][i];
            for (int k = 0; k < j; ++k) {
                y.elements[j][0] -= lower.elements[j][k] * y.elements[k][0];
            }
        }

        // Зворотний хід для знаходження вектора x (Ux = y)
        MTX x(size);
        for (int j = size - 1; j >= 0; --j) {
            x.elements[j][0] = y.elements[j][0];
            for (int k = j + 1; k < size; ++k) {
                x.elements[j][0] -= upper.elements[j][k] * x.elements[k][0];
            }
            x.elements[j][0] /= upper.elements[j][j];
        }

        // Заповнення стовпця оберненої матриці
        for (int j = 0; j < size; ++j) {
            inverse.elements[j][i] = x.elements[j][0];
        }
    }

    return inverse;
}

int main() {
    int size;
    cout << "Enter the size of the matrix (must be a power of 2): ";
    cin >> size;

    if ((size & (size - 1)) != 0 || size <= 0) {
        cout << "Matrix size must be a power of 2." << endl;
        return 1;
    }

    MTX inputMatrix(size);
    cout << "Enter elements of the matrix:\n";
    for (int i = 0; i < size; ++i) {
        for (int j = 0; j < size; ++j) {
            cin >> inputMatrix.elements[i][j];
        }
    }

    try {
        MTX inverseMatrix = computeInverseLU(inputMatrix);
        cout << "\nThe inverse of the matrix is:\n";
        for (int i = 0; i < size; ++i) {
            for (int j = 0; j < size; ++j) {
                cout << fixed << setprecision(6) << inverseMatrix.elements[i][j] << " ";
            }
            cout << endl;
        }
    } catch (const runtime_error& e) {
        cout << e.what() << endl;
    }

    return 0;
}
