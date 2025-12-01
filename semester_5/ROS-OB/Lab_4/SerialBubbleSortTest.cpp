/*
* SerialBubbleSortTest.cpp
 * Допоміжні функції для тестування послідовної версії
 */

#include <cstdio>
#include <algorithm>

using namespace std;

// Функція для форматованого виведення даних
void PrintData(double *pData, int DataSize) {
    for(int i = 0; i < DataSize; i++)
        printf("%7.4f ", pData[i]);
    printf("\n");
}

// Сортування алгоритмом зі стандартної бібліотеки (для порівняння швидкості)
void SerialStdSort(double *pData, int DataSize) {
    sort(pData, pData + DataSize);
}