#include <iostream>
#include <iomanip>
#include <stdexcept>
#include <cmath>
using namespace std;

const double EPSILON = 1e-9; // Поріг для перевірки малих значень

// Структура для представлення матриці
struct Matrix {
    int size; // Розмір матриці
    double** elements; // Двовимірний масив для зберігання елементів матриці

    // Конструктор для створення матриці
    Matrix(int size) {
        this->size = size;
        elements = new double*[size];
        for (int i = 0; i < size; i++)
            elements[i] = new double[size]();
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
Matrix padMatrix(Matrix& original) {
    int newSize = nextPowerOf2(original.size);
    Matrix padded(newSize);
    for (int i = 0; i < original.size; ++i) {
        for (int j = 0; j < original.size; ++j) {
            padded.elements[i][j] = original.elements[i][j]; // Копіюємо елементи
        }
    }
    return padded; // Завжди повертаємо нову матрицю
}

// Функція для видалення нульових доповнень після обчислення оберненої матриці
Matrix trimMatrix(Matrix& padded, int originalSize) {
    Matrix trimmed(originalSize);
    for (int i = 0; i < originalSize; ++i) {
        for (int j = 0; j < originalSize; ++j) {
            trimmed.elements[i][j] = padded.elements[i][j]; // Копіюємо лише необхідну частину
        }
    }
    return trimmed;
}

// Функція для додавання двох матриць
Matrix addMatrices(Matrix A, Matrix B) {
    Matrix C(A.size);
    for (int i = 0; i < A.size; i++) {
        for (int j = 0; j < A.size; j++) {
            C.elements[i][j] = A.elements[i][j] + B.elements[i][j];
        }
    }
    return C;
}

// Функція для віднімання двох матриць
Matrix subtractMatrices(Matrix A, Matrix B) {
    Matrix C(A.size);
    for (int i = 0; i < A.size; i++) {
        for (int j = 0; j < A.size; j++) {
            C.elements[i][j] = A.elements[i][j] - B.elements[i][j];
        }
    }
    return C;
}

// Функція для розбиття матриці на підматриці
Matrix splitMatrix(Matrix A, int startRow, int startCol) {
    int halfSize = A.size / 2;
    Matrix subMatrix(halfSize);
    for (int i = 0; i < halfSize; i++) {
        for (int j = 0; j < halfSize; j++) {
            subMatrix.elements[i][j] = A.elements[startRow + i][startCol + j];
        }
    }
    return subMatrix;
}

// Функція для заповнення підматриці в матрицю
Matrix fillSubMatrix(Matrix C, Matrix subMatrix, int startRow, int startCol) {
    for (int i = 0; i < subMatrix.size; i++) {
        for (int j = 0; j < subMatrix.size; j++) {
            C.elements[i + startRow][j + startCol] = subMatrix.elements[i][j];
        }
    }
    return C;
}

// Просте множення матриць
Matrix simpleMultiply(Matrix A, Matrix B) {
    Matrix C(A.size);
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
Matrix strassenMultiply(Matrix A, Matrix B) {
    if (A.size == 2) {
        return simpleMultiply(A, B); // Базовий випадок для малих матриць
    }

    int halfSize = A.size / 2;

    // Розбиття матриць на підматриці
    Matrix A11 = splitMatrix(A, 0, 0);
    Matrix A12 = splitMatrix(A, 0, halfSize);
    Matrix A21 = splitMatrix(A, halfSize, 0);
    Matrix A22 = splitMatrix(A, halfSize, halfSize);
    Matrix B11 = splitMatrix(B, 0, 0);
    Matrix B12 = splitMatrix(B, 0, halfSize);
    Matrix B21 = splitMatrix(B, halfSize, 0);
    Matrix B22 = splitMatrix(B, halfSize, halfSize);

    // Обчислення проміжних матриць
    Matrix M1 = strassenMultiply(addMatrices(A11, A22), addMatrices(B11, B22));
    Matrix M2 = strassenMultiply(addMatrices(A21, A22), B11);
    Matrix M3 = strassenMultiply(A11, subtractMatrices(B12, B22));
    Matrix M4 = strassenMultiply(A22, subtractMatrices(B21, B11));
    Matrix M5 = strassenMultiply(addMatrices(A11, A12), B22);
    Matrix M6 = strassenMultiply(subtractMatrices(A21, A11), addMatrices(B11, B12));
    Matrix M7 = strassenMultiply(subtractMatrices(A12, A22), addMatrices(B21, B22));

    // Комбінування результатів
    Matrix C(A.size);
    Matrix C11 = subtractMatrices(addMatrices(addMatrices(M1, M4), M7), M5);
    Matrix C12 = addMatrices(M3, M5);
    Matrix C21 = addMatrices(M2, M4);
    Matrix C22 = subtractMatrices(addMatrices(addMatrices(M1, M3), M6), M2);

    // Заповнення підматриць у результат
    C = fillSubMatrix(C, C11, 0, 0);
    C = fillSubMatrix(C, C12, 0, halfSize);
    C = fillSubMatrix(C, C21, halfSize, 0);
    C = fillSubMatrix(C, C22, halfSize, halfSize);

    return C;
}

// Функція для знаходження оберненої матриці за допомогою LU-розкладу
Matrix computeInverseLU(Matrix inputMatrix, int originalSize) {
    int size = inputMatrix.size;
    Matrix lower(size);
    Matrix upper(size);
    Matrix inverse(size);

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
        // Верхня трикутна матриця U
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

        // Нижня трикутна матриця L
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
        Matrix identity(size);
        identity.elements[i][i] = 1;

        // Прямий хід для знаходження вектора y (Ly = e)
        Matrix y(size);
        for (int j = 0; j < originalSize; ++j) {
            y.elements[j][0] = identity.elements[j][i];
            for (int k = 0; k < j; ++k) {
                y.elements[j][0] -= lower.elements[j][k] * y.elements[k][0];
            }
        }

        // Зворотний хід для знаходження вектора x (Ux = y)
        Matrix x(size);
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

    Matrix inputMatrix(size);
    cout << "Enter elements of the matrix:\n";
    for (int i = 0; i < size; ++i) {
        for (int j = 0; j < size; ++j) {
            cin >> inputMatrix.elements[i][j];
        }
    }

    Matrix paddedMatrix = padMatrix(inputMatrix);

    try {
        Matrix inverseMatrix = computeInverseLU(paddedMatrix, size);
        Matrix trimmedInverse = trimMatrix(inverseMatrix, size);
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
