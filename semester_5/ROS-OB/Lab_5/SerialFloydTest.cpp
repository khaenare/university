#include <cstdio>

using namespace std;

// Функція для форматованого виводу матриці
void PrintMatrix(int* pMatrix, int RowCount, int ColCount) {
    for (int i = 0; i < RowCount; i++) {
        for (int j = 0; j < ColCount; j++) {
            printf("%7d", pMatrix[i * ColCount + j]);
        }
        printf("\n");
    }
}//
// Created by Matvii Liashenko on 01.12.2025.
//
