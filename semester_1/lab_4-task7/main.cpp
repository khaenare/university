// написати код, який перевіряє, чи можливо відсорувати масиви за допомогою однієї перестановки, і якщо можливо, то виконує її

#include <iostream>
using namespace std;

void bubbleSort(int firstArr[], int secArr[], int lenght){
    for (int i = 0; i < lenght - 1; i++)

        for (int j = 0; j < lenght - i - 1; j++)
            if (firstArr[j] > firstArr[j + 1]){
                swap(firstArr[j], firstArr[j + 1]);
                swap(secArr[j], secArr[j + 1]);}

}
void bubbleSort(int firstArr[]){
    int lenght = sizeof(firstArr) / sizeof(firstArr[0]);

    for (int i = 0; i < lenght - 1; i++)

        for (int j = 0; j < lenght - i - 1; j++)

            if (firstArr[j] > firstArr[j + 1]){
                swap(firstArr[j], firstArr[j + 1]);}
}
void coutArr(int arr[], int size)
{
    int i;
    for (i = 0; i < size; i++)
        cout << arr[i] << " ";
    cout << endl;
}
bool isSorted(int firstArr[], int secArr[], int lenght){
    for (int i = 0; i < lenght - 1; i++) {
        if (firstArr[i] > firstArr[i + 1]) {
            return false;
        }
    }
    for (int i = 0; i < lenght - 1; i++) {
        if (secArr[i] > secArr[i + 1]) {
            return false;
        }
    }
    return true;
}
int main(){
    int firstArr[]  = { 0,100,50, 200 , 300 , 400};
    int secondArr[] = { 1, 2, 2, 3 ,4 , 5};

    int lenght = sizeof(firstArr) / sizeof(firstArr[0]);

    bubbleSort(firstArr, secondArr, lenght);
    bubbleSort(secondArr, firstArr, lenght);

    if (isSorted(firstArr, secondArr, lenght)){
        coutArr(firstArr, lenght);
        coutArr(secondArr, lenght);
    } else cout << "There is no any possibles sorts" << endl;

    return 0;
}
