/*
* ParallelBubbleSortTest.cpp
 * Допоміжні функції для паралельної версії
 */

#include <cstdio>
#include <cstdlib>
#include <algorithm>

using namespace std;

// Функція для копіювання даних (для створення еталону)
void CopyData(double *pData, int DataSize, double *pDataCopy) {
    copy(pData, pData + DataSize, pDataCopy);
}

// Функція для порівняння двох масивів (перевірка коректності)
bool CompareData(double *pData1, double *pData2, int DataSize) {
    return equal(pData1, pData1 + DataSize, pData2);
}

// Послідовне бульбашкове сортування (використовується процесами локально)
void SerialBubbleSort(double *pData, int DataSize) {
    double Tmp;
    for(int i = 1; i < DataSize; i++)
        for(int j = 0; j < DataSize - i; j++)
            if (pData[j] > pData[j + 1]) {
                Tmp = pData[j];
                pData[j] = pData[j + 1];
                pData[j + 1] = Tmp;
            }
}

// Стандартне сортування (можна використовувати для прискорення локальної частини)
void SerialStdSort(double *pData, int DataSize) {
    sort(pData, pData + DataSize);
}

// Функція для форматованого виведення
void PrintData(double *pData, int DataSize) {
    for(int i = 0; i < DataSize; i++)
        printf("%7.4f ", pData[i]);
    printf("\n");
}