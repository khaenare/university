/*
 * SerialBubbleSort.cpp
 * Головний файл послідовної версії
 */

#include <cstdlib>
#include <cstdio>
#include <cstring>
#include <ctime>
#include <algorithm> // Потрібно для std::copy

using namespace std;

const double RandomDataMultiplier = 1000.0;

// --- Forward declarations (Оголошення функцій з файлу SerialBubbleSortTest.cpp) ---
void PrintData(double *pData, int DataSize);
void SerialStdSort(double *pData, int DataSize);
// ----------------------------------------------------------------------------------

// Функція для виділення пам'яті та встановлення розміру даних
void ProcessInitialization(double *&pData, int& DataSize) {
    do {
        printf("Enter the size of data to be sorted: ");
        scanf("%d", &DataSize);
        if (DataSize <= 0)
            printf("Data size should be greater than zero\n");
    } while (DataSize <= 0);

    printf("Sorting %d data items\n", DataSize);
    pData = new double[DataSize];
}

// Функція завершення процесу (звільнення пам'яті)
void ProcessTermination(double *pData) {
    delete [] pData;
}

// Функція для ініціалізації масиву випадковими числами
void RandomDataInitialization(double *pData, int DataSize) {
    srand((unsigned)time(0)); // Ініціалізація генератора випадкових чисел поточним часом
    for(int i = 0; i < DataSize; i++)
        pData[i] = double(rand()) / RAND_MAX * RandomDataMultiplier;
}

// Алгоритм послідовного бульбашкового сортування
void SerialBubble(double *pData, int DataSize) {
    double Tmp;
    for(int i = 1; i < DataSize; i++)
        for(int j = 0; j < DataSize - i; j++)
            if (pData[j] > pData[j + 1]) {
                Tmp = pData[j];
                pData[j] = pData[j + 1];
                pData[j + 1] = Tmp;
            }
}

int main(int argc, char *argv[]) {
    double *pData = 0;
    double *pDataCopy = 0; // Вказівник для копії масиву
    int DataSize = 0;
    time_t start, finish;
    double duration = 0.0;

    printf("Serial bubble sort program\n");

    // 1. Ініціалізація процесу (введення розміру та виділення пам'яті)
    ProcessInitialization(pData, DataSize);

    // 2. Генерація випадкових даних
    RandomDataInitialization(pData, DataSize);

    // 3. Створення копії даних для другого тесту
    pDataCopy = new double[DataSize];
    copy(pData, pData + DataSize, pDataCopy);

    // --- ТЕСТ 1: Bubble Sort (Ваш алгоритм) ---
    start = clock();
    SerialBubble(pData, DataSize);
    finish = clock();

    duration = (finish - start) / double(CLOCKS_PER_SEC);
    printf("Time of execution (Bubble Sort): %f\n", duration);


    // --- ТЕСТ 2: Standard Sort (Бібліотечний алгоритм) ---
    start = clock();
    SerialStdSort(pDataCopy, DataSize); // Сортуємо копію
    finish = clock();

    duration = (finish - start) / double(CLOCKS_PER_SEC);
    printf("Time of execution (Standard Sort): %f\n", duration);

    // 4. Завершення процесу (очищення пам'яті)
    ProcessTermination(pData);
    delete [] pDataCopy;

    return 0;
}