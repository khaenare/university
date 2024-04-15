#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <random>
using namespace std;

struct Point3D {
    double x, y, z;
    double distance() const {
        return sqrt(x*x + y*y + z*z);
    }
};
vector<Point3D> generateRandomPoints(size_t size) {
    random_device rd;
    mt19937 gen(rd());
    uniform_real_distribution<> dis(-100.0, 100.0);

    vector<Point3D> points(size);
    for (Point3D& point : points) {
        point.x = dis(gen);
        point.y = dis(gen);
        point.z = dis(gen);
    }
    return points;
}
bool operator<(const Point3D& a, const Point3D& b) {
    return a.distance() < b.distance();
}

void printPoints(const vector<Point3D>& points);

void InsertionSort(vector<Point3D>& points);
int  partition(vector<Point3D>& points, int low, int high);
void QuickSort(vector<Point3D>& points, int low, int high);
void merge(vector<Point3D>& points, int left, int mid, int right);
void MergeSort(vector<Point3D>& points);
void CombinatedSort(vector<Point3D>& points);

void demonstrationMode();
void benchmarkMode();


int main() {
    int mode;
    cout << "Select mode:\n1. Demonstration mode \n2. Benchmark mode:\nEnter a number of mode: ";
    cin >> mode;

    switch (mode) {
        case 1:
            demonstrationMode();
            break;
        case 2:
            //benchmarkMode();
            break;
        default:
            cerr << "Error! You enter incorrect mode\n";
            break;
    }
    return 0;
}

void demonstrationMode() {
    size_t n;
    cout << "Enter the number of dots to generate: ";
    cin >> n;
    cout << "\n";

    // InsertionSort
    vector<Point3D> pointsInsertion = generateRandomPoints(n);
    cout << "Unsorted array of dots for Insertion Sort:" << endl;
    printPoints(pointsInsertion);
    InsertionSort(pointsInsertion);
    cout << "Sorted array of dots (Insertion Sort):" << endl;
    printPoints(pointsInsertion);
    cout << "\n";

    // QuickSort
    vector<Point3D> pointsQuickSort = generateRandomPoints(n);
    cout << "Unsorted array of dots for Quicksort:" << endl;
    printPoints(pointsQuickSort);
    QuickSort(pointsQuickSort, 0, pointsQuickSort.size() - 1);
    cout << "Sorted array of dots (QuickSort):" << endl;
    printPoints(pointsQuickSort);
    cout << "\n";

    //MergeSort
    vector<Point3D> pointsMergeSort = generateRandomPoints(n);
    cout << "Unsorted array of dots for MergeSort (Bottom-Up):" << endl;
    printPoints(pointsMergeSort);
    MergeSort(pointsMergeSort);
    cout << "Sorted array of dots for MergeSort (Bottom-Up):" << endl;
    printPoints(pointsMergeSort);
    cout << "\n";


    //CombinedSort
    vector<Point3D> pointsCombinedSort = generateRandomPoints(n);
    cout << "Unsorted array of dots for CombinedSort:" << endl;
    printPoints(pointsCombinedSort);
    CombinatedSort(pointsCombinedSort);
    cout << "Sorted array of dots for CombinedSort:" << endl;
    printPoints(pointsCombinedSort);
    cout << "\n";


    //StandartSort
    vector<Point3D> pointsStandartSort = generateRandomPoints(n);
    cout << "Unsorted array of dots for StandartSort:" << endl;
    printPoints(pointsStandartSort);
    sort(pointsStandartSort.begin(), pointsStandartSort.end());
    cout << "Sorted array of dots for StandartSort:" << endl;
    printPoints(pointsStandartSort);
    cout << "\n";
}
void benchmarkMode(){}

void InsertionSort(vector<Point3D>& points) {
    int n = points.size();
    for (int i = 1; i < n; i++) {
        Point3D key = points[i];
        int j = i - 1;

        while (j >= 0 && points[j].distance() > key.distance()) {
            points[j + 1] = points[j];
            j = j - 1;
        }
        points[j + 1] = key;
    }
}
void CombinatedSort(vector<Point3D>& points){
    int length = points.size();
    if (length < 50 ){
        InsertionSort(points);
    } else QuickSort(points, 0, length-1);
}

void QuickSort(vector<Point3D>& points, int low, int high) {
    if (low < high) {
        int pi = partition(points, low, high);

        QuickSort(points, low, pi - 1);
        QuickSort(points, pi + 1, high);
    }
}
int partition(vector<Point3D>& points, int low, int high) {
    // Вибір середнього індексу як pivot
    int pivotIndex = low + (high - low) / 2;
    swap(points[pivotIndex], points[high]);
    Point3D pivot = points[high];
    int i = low - 1;

    for (int j = low; j <= high - 1; j++) {
        if (points[j].distance() <= pivot.distance()) {
            i++;
            swap(points[i], points[j]);
        }
    }
    swap(points[i + 1], points[high]);
    return i + 1;
}

void MergeSort(vector<Point3D>& points) {
    int n = points.size();
    for (int width = 1; width < n; width = 2 * width) {
        for (int i = 0; i < n; i = i + 2 * width) {
            int mid = min(i + width - 1, n - 1);
            int right = min(i + 2 * width - 1, n - 1);
            merge(points, i, mid, right);
        }
    }
}
void merge(vector<Point3D>& points, int left, int mid, int right) {
    int n1 = mid - left + 1;
    int n2 = right - mid;
    vector<Point3D> L(n1), R(n2);

    for (int i = 0; i < n1; i++)
        L[i] = points[left + i];
    for (int j = 0; j < n2; j++)
        R[j] = points[mid + 1 + j];

    int i = 0;
    int j = 0;
    int k = left;

    while (i < n1 && j < n2) {
        if (L[i].distance() <= R[j].distance()) {
            points[k] = L[i];
            i++;
        } else {
            points[k] = R[j];
            j++;
        }
        k++;
    }

    while (i < n1) {
        points[k] = L[i];
        i++;
        k++;
    }

    while (j < n2) {
        points[k] = R[j];
        j++;
        k++;
    }
}

void printPoints(const vector<Point3D>& points) {
    for (const auto& point : points) {
        cout << "(" << point.x << ", " << point.y << ", " << point.z << ") -> Distance: " << point.distance() << endl;
    }
}
