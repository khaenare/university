//Вилучити з тексту всі слова, які містять у собі паліндроми довжиною не менші за n. Записати результуючий текст у інший файл.
#include <iostream>
#include <fstream>
#include <string>
//#include <sstream>
using namespace std;

const string pathforInput = "../input.txt";
const string pathforOutput = "../output.txt";
const int minPalindromeLenthToDelete = 3;

bool isPalindrome(string word) {
    int length = word.length();
    int left = 0;
    int right = length - 1;

    if (length == 1 || length < minPalindromeLenthToDelete) return false;

    while (left < right) {
        if (word[left] != word[right])
            return false;
        left++;
        right--;
    }
    return true;
}

string removePalindromesInsideWords(string word) {
    string result = "";
    int wordLength = word.length();
    int start = 0;
    int end = 0;

    while (end < wordLength) {
        string substring = word.substr(start, end - start + 1);
        if (isPalindrome(substring)) {
            start = end + 1;
        } else {
            result += word[end];
        }
        end++;
    }

    return result;
}

int main() {
    //Проверка на открытие
    ifstream inputFile;
    inputFile.open(pathforInput);
    if (!inputFile.is_open()) {
        cerr << "Unable to open input file!\n";
        return 1;
    }
    ofstream outputFile;
    outputFile.open(pathforOutput);
    if (!outputFile.is_open()) {
        cerr << "Unable to create output file!\n";
        return 1;
    }
    //Проверка на открытие

    string curLine;
    while (getline(inputFile, curLine)) {
        istringstream everyLine(curLine);
        string word;

        while (everyLine >> word) {
            string modifiedWord = removePalindromesInsideWords(word);
            outputFile << modifiedWord << " ";
        }
        outputFile << "\n";
    }

    inputFile.close();
    outputFile.close();

    cout << "Palindromes removed successfully!\n";

    return 0;
}
