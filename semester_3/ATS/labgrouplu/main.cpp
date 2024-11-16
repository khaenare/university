#include <iostream>
#include <iomanip>
#include <stdexcept>
#include <cmath>
using namespace std;

const double EPSILON = 1e-9; // Поріг для перевірки малих значень

// Структура для представлення матриці
template <typename T>
struct Matrix {
    int size; // Розмір матриці
    T** elements; // Двовимірний масив для зберігання елементів матриці

    // Конструктор для створення матриці
    Matrix(int size) : size(size) {
        elements = new T*[size];
        for (int i = 0; i < size; i++)
            elements[i] = new T[size]();
    }

    // Деструктор для звільнення пам'яті
    ~Matrix() {
        for (int i = 0; i < size; ++i)
            delete[] elements[i];
        delete[] elements;
    }
};

// Функція для визначення найближчого степеня 2, який більший або дорівнює даному числу
int nextPowerOf2(int n) {
    if (n <= 0) return 1;
    int power = 1;
    while (power < n) power *= 2;
    return power;
}

// Функція для доповнення матриці до найближчого розміру, який є степенем 2
template <typename T>
Matrix<T> padMatrix(Matrix<T>& original) {
    int newSize = nextPowerOf2(original.size);
    Matrix<T> padded(newSize);
    for (int i = 0; i < original.size; ++i) {
        for (int j = 0; j < original.size; ++j) {
            padded.elements[i][j] = original.elements[i][j]; // Копіюємо елементи
        }
    }
    return padded; // Завжди повертаємо нову матрицю
}

// Функція для видалення нульових доповнень після обчислення оберненої матриці
template <typename T>
Matrix<T> trimMatrix(Matrix<T>& padded, int originalSize) {
    Matrix<T> trimmed(originalSize);
    for (int i = 0; i < originalSize; ++i) {
        for (int j = 0; j < originalSize; ++j) {
            trimmed.elements[i][j] = padded.elements[i][j]; // Копіюємо лише необхідну частину
        }
    }
    return trimmed;
}

// Заповнення підматриці у більшу матрицю
template <typename T>
Matrix<T> fillSubMatrix(Matrix<T> C, Matrix<T> subMatrix, int startRow, int startCol) {
    for (int i = 0; i < subMatrix.size; i++) {
        for (int j = 0; j < subMatrix.size; j++) {
            C.elements[i + startRow][j + startCol] = subMatrix.elements[i][j];
        }
    }
    return C;
}

// Просте множення матриць
template <typename T>
Matrix<T> simpleMultiply(Matrix<T> A, Matrix<T> B) {
    Matrix<T> C(A.size);
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
template <typename T>
Matrix<T> strassenMultiply(Matrix<T> A, Matrix<T> B) {
    if (A.size == 2) {
        return simpleMultiply(A, B);
    }

    int halfSize = A.size / 2;

    Matrix<T> A11 = splitMatrix(A, 0, 0);
    Matrix<T> A12 = splitMatrix(A, 0, halfSize);
    Matrix<T> A21 = splitMatrix(A, halfSize, 0);
    Matrix<T> A22 = splitMatrix(A, halfSize, halfSize);
    Matrix<T> B11 = splitMatrix(B, 0, 0);
    Matrix<T> B12 = splitMatrix(B, 0, halfSize);
    Matrix<T> B21 = splitMatrix(B, halfSize, 0);
    Matrix<T> B22 = splitMatrix(B, halfSize, halfSize);

    Matrix<T> M1 = strassenMultiply(addMatrices(A11, A22), addMatrices(B11, B22));
    Matrix<T> M2 = strassenMultiply(addMatrices(A21, A22), B11);
    Matrix<T> M3 = strassenMultiply(A11, subtractMatrices(B12, B22));
    Matrix<T> M4 = strassenMultiply(A22, subtractMatrices(B21, B11));
    Matrix<T> M5 = strassenMultiply(addMatrices(A11, A12), B22);
    Matrix<T> M6 = strassenMultiply(subtractMatrices(A21, A11), addMatrices(B11, B12));
    Matrix<T> M7 = strassenMultiply(subtractMatrices(A12, A22), addMatrices(B21, B22));

    Matrix<T> C(A.size);
    Matrix<T> C11 = subtractMatrices(addMatrices(addMatrices(M1, M4), M7), M5);
    Matrix<T> C12 = addMatrices(M3, M5);
    Matrix<T> C21 = addMatrices(M2, M4);
    Matrix<T> C22 = subtractMatrices(addMatrices(addMatrices(M1, M3), M6), M2);

    C = fillSubMatrix(C, C11, 0, 0);
    C = fillSubMatrix(C, C12, 0, halfSize);
    C = fillSubMatrix(C, C21, halfSize, 0);
    C = fillSubMatrix(C, C22, halfSize, halfSize);

    return C;
}

// Функція для знаходження оберненої матриці за допомогою LU-розкладу
template <typename T>
Matrix<T> computeInverseLU(Matrix<T> inputMatrix, int originalSize) {
    int size = inputMatrix.size;
    Matrix<T> lower(size);
    Matrix<T> upper(size);
    Matrix<T> inverse(size);

    // Ініціалізація матриць L та U
    for (int i = 0; i < size; ++i) {
        for (int j = 0; j < size; ++j) {
            lower.elements[i][j] = (i == j) ? 1 : 0;
            upper.elements[i][j] = 0;
            inverse.elements[i][j] = 0;
        }
    }

    // LU-розклад
    for (int i = 0; i < originalSize; ++i) {
        // Визначення верхньої трикутної матриці U
        for (int j = i; j < originalSize; ++j) {
            upper.elements[i][j] = inputMatrix.elements[i][j];
            for (int k = 0; k < i; ++k) {
                upper.elements[i][j] -= lower.elements[i][k] * upper.elements[k][j];
            }
        }

        // Перевірка на майже нульовий елемент
        if (abs(upper.elements[i][i]) < EPSILON) {
            throw runtime_error("Matrix is nearly singular and cannot be inverted.");
        }

        // Визначення нижньої трикутної матриці L
        for (int j = i + 1; j < originalSize; ++j) {
            lower.elements[j][i] = inputMatrix.elements[j][i];
            for (int k = 0; k < i; ++k) {
                lower.elements[j][i] -= lower.elements[j][k] * upper.elements[k][i];
            }
            lower.elements[j][i] /= upper.elements[i][i];
        }
    }

    // Знаходження оберненої матриці за допомогою прямої та зворотної підстановки
    for (int i = 0; i < originalSize; ++i) {
        Matrix<T> identity(size);
        identity.elements[i][i] = 1;

        // Прямий хід для знаходження вектора y (Ly = e)
        Matrix<T> y(size);
        for (int j = 0; j < originalSize; ++j) {
            y.elements[j][0] = identity.elements[j][i];
            for (int k = 0; k < j; ++k) {
                y.elements[j][0] -= lower.elements[j][k] * y.elements[k][0];
            }
        }

        // Зворотний хід для знаходження вектора x (Ux = y)
        Matrix<T> x(size);
        for (int j = originalSize - 1; j >= 0; --j) {
            x.elements[j][0] = y.elements[j][0];
            for (int k = j + 1; k < originalSize; ++k) {
                x.elements[j][0] -= upper.elements[j][k] * x.elements[k][0];
            }
            x.elements[j][0] /= upper.elements[j][j];
        }

        // Заповнення стовпця оберненої матриці
        for (int j = 0; j < originalSize; ++j) {
            inverse.elements[j][i] = x.elements[j][0];
        }
    }

    return inverse;
}

int main() {
    int size;
    cout << "Enter the size of the matrix: ";
    cin >> size;

    if (size <= 0) {
        cout << "Matrix size must be a positive integer." << endl;
        return 1;
    }

    Matrix<double> inputMatrix(size);
    cout << "Enter elements of the matrix:\n";
    for (int i = 0; i < size; ++i) {
        for (int j = 0; j < size; ++j) {
            cin >> inputMatrix.elements[i][j];
        }
    }

    Matrix<double> paddedMatrix = padMatrix(inputMatrix);

    try {
        Matrix<double> inverseMatrix = computeInverseLU(paddedMatrix, size);
        Matrix<double> trimmedInverse = trimMatrix(inverseMatrix, size);
        cout << "\nThe inverse of the matrix is:\n";
        for (int i = 0; i < size; ++i) {
            for (int j = 0; j < size; ++j) {
                cout << fixed << setprecision(6) << trimmedInverse.elements[i][j] << " ";
            }
            cout << endl;
        }
    } catch (const runtime_error& e) {
        cout << e.what() << endl;
    }

    return 0;
}

