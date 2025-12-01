#include <cstdio>
#include <algorithm>

using namespace std;

// Локальна функція Min для SerialFloyd у цьому файлі
static int Min(int A, int B) {
    int Result = (A < B) ? A : B;
    if ((A < 0) && (B >= 0)) Result = B;
    if ((B < 0) && (A >= 0)) Result = A;
    if ((A < 0) && (B < 0)) Result = -1;
    return Result;
}

// Функція для копіювання матриці
void CopyMatrix(int* pMatrix, int Size, int* pMatrixCopy) {
    copy(pMatrix, pMatrix + Size * Size, pMatrixCopy);
}

// Функція для порівняння матриць
bool CompareMatrices(int* pMatrix1, int* pMatrix2, int Size) {
    return equal(pMatrix1, pMatrix1 + Size * Size, pMatrix2);
}

// Функція для послідовного алгоритму Флойда (для перевірки)
void SerialFloyd(int* pMatrix, int Size) {
    int t1, t2;
    for (int k = 0; k < Size; k++) {
        for (int i = 0; i < Size; i++) {
            for (int j = 0; j < Size; j++) {
                if ((pMatrix[i * Size + k] != -1) && (pMatrix[k * Size + j] != -1)) {
                    t1 = pMatrix[i * Size + j];
                    t2 = pMatrix[i * Size + k] + pMatrix[k * Size + j];
                    pMatrix[i * Size + j] = Min(t1, t2);
                }
            }
        }
    }
}

// Функція для форматованого виводу матриці
void PrintMatrix(int* pMatrix, int RowCount, int ColCount) {
    for (int i = 0; i < RowCount; i++) {
        for (int j = 0; j < ColCount; j++) {
            printf("%7d", pMatrix[i * ColCount + j]);
        }
        printf("\n");
    }
}