/*
Блок 0: 1, 3
Блок 1: 5
Блок 2: 11
Блок 3: 14
Блок 4: 18
Блок 5: 20
Блок 6: 21
*/

#include <iostream>
#include <vector>
#include <queue>
#include <stack>
#include <bitset>
#include <algorithm>
#include <limits>
#include <set>
#include <cstdlib>
#include <chrono>


using namespace std;
using namespace std::chrono;

const int INF = numeric_limits<int>::max();


struct GraphMatrix {
    vector<vector<int>> adjMatrix;
    int numVertices;

    GraphMatrix(int vertices) : numVertices(vertices) {
        adjMatrix.resize(vertices, vector<int>(vertices, INF));
        for (int i = 0; i < vertices; ++i) {
            adjMatrix[i][i] = 0;
        }
    }
};

struct GraphBitVector {
    vector<bitset<32>> adjBitVector;
    int numVertices;

    GraphBitVector(int vertices) : numVertices(vertices) {
        adjBitVector.resize(vertices);
    }
};

struct Edge {
    int src, dest, weight;
};

struct Graph {
    int V, E;
    vector<Edge> edges;
};


void addEdgeMatrix(GraphMatrix& graph, int src, int dest, int weight, bool directed);
void printGraphMatrix(const GraphMatrix& graph);
void addEdgeBitVector(GraphBitVector& graph, int src, int dest, bool directed);
void printGraphBitVector(const GraphBitVector& graph);
void generateRandomGraphMatrix(GraphMatrix& graph, int numEdges, bool directed);
void generateRandomGraphBitVector(GraphBitVector& graph, int numEdges, bool directed);
GraphBitVector convertMatrixToBitVector(const GraphMatrix& matrixGraph);
GraphMatrix convertBitVectorToMatrix(const GraphBitVector& bitVectorGraph);
void DFSMatrixUtil(const GraphMatrix& graph, int vertex, vector<bool>& visited);
void DFSMatrix(const GraphMatrix& graph, int startVertex);
void DFSBitVectorUtil(const GraphBitVector& graph, int vertex, vector<bool>& visited);
void DFSBitVector(const GraphBitVector& graph, int startVertex);
void dijkstraMatrix(const GraphMatrix& graph, int startVertex);
void dijkstraBitVector(const GraphBitVector& graph, int startVertex);
void topologicalSortUtilMatrix(const GraphMatrix& graph, int v, vector<bool>& visited, stack<int>& Stack);
void topologicalSortMatrix(const GraphMatrix& graph);
void topologicalSortUtilBitVector(const GraphBitVector& graph, int v, vector<bool>& visited, stack<int>& Stack);
void topologicalSortBitVector(const GraphBitVector& graph);
void BFSMatrix(const GraphMatrix& graph, int startVertex);
void BFSBitVector(const GraphBitVector& graph, int startVertex);
Graph createGraph(int V, int E);
int find(vector<int>& parent, int i);
void Union(vector<int>& parent, vector<int>& rank, int x, int y);
void KruskalMST(Graph& graph);
void addEdgeKruskal(Graph& graph, int src, int dest, int weight);
bool isConnectedMatrixUtil(const GraphMatrix& graph, int vertex, vector<bool>& visited);
bool isConnectedMatrix(const GraphMatrix& graph);
bool isConnectedBitVectorUtil(const GraphBitVector& graph, int vertex, vector<bool>& visited);
bool isConnectedBitVector(const GraphBitVector& graph);
void BFSForMSTMatrix(const GraphMatrix& graph, int startVertex);
void BFSForMSTBitVector(const GraphBitVector& graph, int startVertex);

void interactiveMode();
void demoMode();
void benchmarkMode();


int main() {
    srand(time(0));
    int mode;
    cout << "Select mode:\n1. Interactive mode \n2. Demonstration mode\n3. Benchmark mode:\nEnter a number of mode: ";
    cin >> mode;

    switch (mode) {
        case 1:
            interactiveMode();
            break;
        case 2:
            demoMode();
            break;
        case 3:
            benchmarkMode();
            break;
        default:
            cerr << "Error! You enter incorrect mode\n";
            break;
    }
    return 0;
}


void interactiveMode() {
    GraphMatrix* matrixGraph = nullptr;
    GraphBitVector* bitVectorGraph = nullptr;
    Graph kruskalGraph;

    while (true) {
        cout << "\nMenu:\n";
        // Блок 0
        cout << "1. Create graph (Matrix) - Block 0\n";
        cout << "2. Create graph (Bit Vector) - Block 0\n";
        cout << "3. Add edge (Matrix) - Block 0\n";
        cout << "4. Add edge (Bit Vector) - Block 0\n";
        cout << "5. Print graph (Matrix) - Block 0\n";
        cout << "6. Print graph (Bit Vector) - Block 0\n";
        cout << "7. Generate random graph (Matrix) - Block 0\n";
        cout << "8. Generate random graph (Bit Vector) - Block 0\n";
        cout << "9. Convert Matrix to Bit Vector - Block 0\n";
        cout << "10. Convert Bit Vector to Matrix - Block 0\n";

        // Блок 1
        cout << "11. Check connectivity (Matrix) - Block 1\n";
        cout << "12. Check connectivity (Bit Vector) - Block 1\n";

        // Блок 2
        cout << "13. DFS (Matrix) - Block 2\n";
        cout << "14. DFS (Bit Vector) - Block 2\n";
        cout << "15. BFS (Matrix) - Block 2\n";
        cout << "16. BFS (Bit Vector) - Block 2\n";

        // Блок 3
        cout << "17. Dijkstra (Matrix) - Block 3\n";
        cout << "18. Dijkstra (Bit Vector) - Block 3\n";

        // Блок 4
        cout << "19. Topological Sort (Matrix) - Block 4\n";
        cout << "20. Topological Sort (Bit Vector) - Block 4\n";

        // Блок 5
        cout << "21. MST using BFS (Matrix) - Block 5\n";
        cout << "22. MST using BFS (Bit Vector) - Block 5\n";

        // Блок 6
        cout << "23. Create graph (Kruskal) - Block 6\n";
        cout << "24. Add edge (Kruskal) - Block 6\n";
        cout << "25. Kruskal (Kruskal) - Block 6\n";

        cout << "0. Exit\n";
        cout << "Enter your choice: ";

        int choice;
        cin >> choice;

        if (choice == 0) break;

        int vertices, edges, src, dest, weight, startVertex;
        bool directed;

        switch (choice) {
            case 1:
                cout << "Enter number of vertices: ";
                cin >> vertices;
                if (matrixGraph) delete matrixGraph;
                matrixGraph = new GraphMatrix(vertices);
                break;
            case 2:
                cout << "Enter number of vertices (<= 32): ";
                cin >> vertices;
                if (bitVectorGraph) delete bitVectorGraph;
                bitVectorGraph = new GraphBitVector(vertices);
                break;
            case 3:
                cout << "Enter source, destination, weight, and directed (1/0): ";
                cin >> src >> dest >> weight >> directed;
                addEdgeMatrix(*matrixGraph, src, dest, weight, directed);
                break;
            case 4:
                cout << "Enter source, destination, and directed (1/0): ";
                cin >> src >> dest >> directed;
                addEdgeBitVector(*bitVectorGraph, src, dest, directed);
                break;
            case 5:
                if (matrixGraph) {
                    printGraphMatrix(*matrixGraph);
                } else {
                    cout << "Matrix graph not created.\n";
                }
                break;
            case 6:
                if (bitVectorGraph) {
                    printGraphBitVector(*bitVectorGraph);
                } else {
                    cout << "Bit Vector graph not created.\n";
                }
                break;
            case 7:
                cout << "Enter number of edges and directed (1/0): ";
                cin >> edges >> directed;
                if (matrixGraph) {
                    generateRandomGraphMatrix(*matrixGraph, edges, directed);
                } else {
                    cout << "Matrix graph not created.\n";
                }
                break;
            case 8:
                cout << "Enter number of edges and directed (1/0): ";
                cin >> edges >> directed;
                if (bitVectorGraph) {
                    generateRandomGraphBitVector(*bitVectorGraph, edges, directed);
                } else {
                    cout << "Bit Vector graph not created.\n";
                }
                break;
            case 9:
                if (matrixGraph) {
                    GraphBitVector converted = convertMatrixToBitVector(*matrixGraph);
                    printGraphBitVector(converted);
                }
                break;
            case 10:
                if (bitVectorGraph) {
                    GraphMatrix converted = convertBitVectorToMatrix(*bitVectorGraph);
                    printGraphMatrix(converted);
                }
                break;
            case 11:
                if (matrixGraph) {
                    if (isConnectedMatrix(*matrixGraph)) {
                        cout << "Graph is connected.\n";
                    } else {
                        cout << "Graph is not connected.\n";
                    }
                } else {
                    cout << "Matrix graph not created.\n";
                }
                break;
            case 12:
                if (bitVectorGraph) {
                    if (isConnectedBitVector(*bitVectorGraph)) {
                        cout << "Graph is connected.\n";
                    } else {
                        cout << "Graph is not connected.\n";
                    }
                } else {
                    cout << "Bit Vector graph not created.\n";
                }
                break;
            case 13:
                if (matrixGraph) {
                    cout << "Enter start vertex: ";
                    cin >> startVertex;
                    DFSMatrix(*matrixGraph, startVertex);
                } else {
                    cout << "Matrix graph not created.\n";
                }
                break;
            case 14:
                if (bitVectorGraph) {
                    cout << "Enter start vertex: ";
                    cin >> startVertex;
                    DFSBitVector(*bitVectorGraph, startVertex);
                } else {
                    cout << "Bit Vector graph not created.\n";
                }
                break;
            case 15:
                if (matrixGraph) {
                    cout << "Enter start vertex: ";
                    cin >> startVertex;
                    BFSMatrix(*matrixGraph, startVertex);
                } else {
                    cout << "Matrix graph не створено.\n";
                }
                break;
            case 16:
                if (bitVectorGraph) {
                    cout << "Enter start vertex: ";
                    cin >> startVertex;
                    BFSBitVector(*bitVectorGraph, startVertex);
                } else {
                    cout << "Bit Vector graph не створено.\n";
                }
                break;
            case 17:
                if (matrixGraph) {
                    cout << "Enter start vertex: ";
                    cin >> startVertex;
                    dijkstraMatrix(*matrixGraph, startVertex);
                } else {
                    cout << "Matrix graph не створено.\n";
                }
                break;
            case 18:
                if (bitVectorGraph) {
                    cout << "Enter start vertex: ";
                    cin >> startVertex;
                    dijkstraBitVector(*bitVectorGraph, startVertex);
                } else {
                    cout << "Bit Vector graph не створено.\n";
                }
                break;
            case 19:
                if (matrixGraph) {
                    topologicalSortMatrix(*matrixGraph);
                } else {
                    cout << "Matrix graph не створено.\n";
                }
                break;
            case 20:
                if (bitVectorGraph) {
                    topologicalSortBitVector(*bitVectorGraph);
                } else {
                    cout << "Bit Vector graph не створено.\n";
                }
                break;
            case 21:
                if (matrixGraph) {
                    cout << "Enter start vertex: ";
                    cin >> startVertex;
                    BFSForMSTMatrix(*matrixGraph, startVertex);
                } else {
                    cout << "Matrix graph не створено.\n";
                }
                break;
            case 22:
                if (bitVectorGraph) {
                    cout << "Enter start vertex: ";
                    cin >> startVertex;
                    BFSForMSTBitVector(*bitVectorGraph, startVertex);
                } else {
                    cout << "Bit Vector graph не створено.\n";
                }
                break;
            case 23:
                cout << "Enter number of vertices and edges: ";
                cin >> vertices >> edges;
                kruskalGraph = createGraph(vertices, edges);
                break;
            case 24:
                cout << "Enter source, destination, and weight: ";
                cin >> src >> dest >> weight;
                addEdgeKruskal(kruskalGraph, src, dest, weight);
                break;
            case 25:
                if (kruskalGraph.V != 0) {
                    KruskalMST(kruskalGraph);
                } else {
                    cout << "Kruskal graph не створено.\n";
                }
                break;
            default:
                cout << "Invalid choice!\n";
        }
    }

    delete matrixGraph;
    delete bitVectorGraph;
}
void demoMode() {
    // Блок 0: Создание графов и добавление ребер
    cout << "\n=== Demo Mode ===\n";

    GraphMatrix matrixGraph(5);
    addEdgeMatrix(matrixGraph, 0, 1, 2, false);
    addEdgeMatrix(matrixGraph, 0, 4, 8, false);
    addEdgeMatrix(matrixGraph, 1, 2, 3, false);
    addEdgeMatrix(matrixGraph, 1, 3, 7, false);
    addEdgeMatrix(matrixGraph, 2, 3, 1, false);
    addEdgeMatrix(matrixGraph, 3, 4, 2, false);

    cout << "Graph (Matrix Representation):\n";
    printGraphMatrix(matrixGraph);

    GraphBitVector bitVectorGraph(5);
    addEdgeBitVector(bitVectorGraph, 0, 1, false);
    addEdgeBitVector(bitVectorGraph, 0, 4, false);
    addEdgeBitVector(bitVectorGraph, 1, 2, false);
    addEdgeBitVector(bitVectorGraph, 1, 3, false);
    addEdgeBitVector(bitVectorGraph, 2, 3, false);
    addEdgeBitVector(bitVectorGraph, 3, 4, false);

    cout << "Graph (Bit Vector Representation):\n";
    printGraphBitVector(bitVectorGraph);

    // Блок 1: Проверка связности графа
    cout << "Check connectivity (Matrix): " << (isConnectedMatrix(matrixGraph) ? "Connected" : "Not Connected") << endl;
    cout << "Check connectivity (Bit Vector): " << (isConnectedBitVector(bitVectorGraph) ? "Connected" : "Not Connected") << endl;

    // Блок 2: Обход графа в глубину и ширину
    cout << "DFS (Matrix): ";
    DFSMatrix(matrixGraph, 0);

    cout << "DFS (Bit Vector): ";
    DFSBitVector(bitVectorGraph, 0);

    cout << "BFS (Matrix): ";
    BFSMatrix(matrixGraph, 0);

    cout << "BFS (Bit Vector): ";
    BFSBitVector(bitVectorGraph, 0);

    // Блок 3: Алгоритм Дейкстры
    cout << "Dijkstra (Matrix): ";
    dijkstraMatrix(matrixGraph, 0);

    cout << "Dijkstra (Bit Vector): ";
    dijkstraBitVector(bitVectorGraph, 0);

    // Блок 4: Топологическая сортировка
    cout << "Topological Sort (Matrix): ";
    topologicalSortMatrix(matrixGraph);

    cout << "Topological Sort (Bit Vector): ";
    topologicalSortBitVector(bitVectorGraph);

    // Блок 5: Минимальное остовное дерево (на основе BFS)
    cout << "MST using BFS (Matrix): ";
    BFSForMSTMatrix(matrixGraph, 0);

    cout << "MST using BFS (Bit Vector): ";
    BFSForMSTBitVector(bitVectorGraph, 0);

    // Блок 6: Алгоритм Краскала
    Graph kruskalGraph = createGraph(5, 6);
    addEdgeKruskal(kruskalGraph, 0, 1, 2);
    addEdgeKruskal(kruskalGraph, 0, 4, 8);
    addEdgeKruskal(kruskalGraph, 1, 2, 3);
    addEdgeKruskal(kruskalGraph, 1, 3, 7);
    addEdgeKruskal(kruskalGraph, 2, 3, 1);
    addEdgeKruskal(kruskalGraph, 3, 4, 2);

    cout << "Kruskal's MST: ";
    KruskalMST(kruskalGraph);

    cout << "\n=== End of Demo Mode ===\n";
}
void benchmarkMode() {
    const int numVertices = 32;  // Установим лимит в 32 вершины для битового вектора
    const int numEdges = 50;
    cout << "Benchmark mode started for graph with " << numVertices << " vertices and " << numEdges << " edges.\n\n";

    // Подготовка графов
    GraphMatrix matrixGraph(numVertices);
    GraphBitVector bitVectorGraph(numVertices);
    generateRandomGraphMatrix(matrixGraph, numEdges, false);
    generateRandomGraphBitVector(bitVectorGraph, numEdges, false);
    Graph kruskalGraph = createGraph(numVertices, numEdges);
    for (int i = 0; i < numEdges; ++i) {
        addEdgeKruskal(kruskalGraph, rand() % numVertices, rand() % numVertices, rand() % 10 + 1);
    }

    // Время выполнения и использование памяти для каждого алгоритма и представления графа
    auto start = high_resolution_clock::now();
    auto stop = high_resolution_clock::now();
    auto duration = duration_cast<microseconds>(stop - start);

    // Block 1: Проверка связности графа
    cout << "Block 1: Connectivity Check\n";

    start = high_resolution_clock::now();
    isConnectedMatrix(matrixGraph);
    stop = high_resolution_clock::now();
    duration = duration_cast<microseconds>(stop - start);
    cout << "Matrix Connectivity: " << duration.count() << " microseconds\n\n";

    start = high_resolution_clock::now();
    isConnectedBitVector(bitVectorGraph);
    stop = high_resolution_clock::now();
    duration = duration_cast<microseconds>(stop - start);
    cout << "Bit Vector Connectivity: " << duration.count() << " microseconds\n\n";

    // Block 2: Обход графа в глубину и ширину
    cout << "Block 2: Graph Traversal\n";

    start = high_resolution_clock::now();
    DFSMatrix(matrixGraph, 0);
    stop = high_resolution_clock::now();
    duration = duration_cast<microseconds>(stop - start);
    cout << "Matrix DFS: " << duration.count() << " microseconds\n\n";

    start = high_resolution_clock::now();
    DFSBitVector(bitVectorGraph, 0);
    stop = high_resolution_clock::now();
    duration = duration_cast<microseconds>(stop - start);
    cout << "Bit Vector DFS: " << duration.count() << " microseconds\n\n";

    start = high_resolution_clock::now();
    BFSMatrix(matrixGraph, 0);
    stop = high_resolution_clock::now();
    duration = duration_cast<microseconds>(stop - start);
    cout << "Matrix BFS: " << duration.count() << " microseconds\n\n";

    start = high_resolution_clock::now();
    BFSBitVector(bitVectorGraph, 0);
    stop = high_resolution_clock::now();
    duration = duration_cast<microseconds>(stop - start);
    cout << "Bit Vector BFS: " << duration.count() << " microseconds\n\n";

    // Block 3: Алгоритм Дейкстры
    cout << "Block 3: Dijkstra's Algorithm\n";

    start = high_resolution_clock::now();
    dijkstraMatrix(matrixGraph, 0);
    stop = high_resolution_clock::now();
    duration = duration_cast<microseconds>(stop - start);
    cout << "Matrix Dijkstra: " << duration.count() << " microseconds\n\n";

    start = high_resolution_clock::now();
    dijkstraBitVector(bitVectorGraph, 0);
    stop = high_resolution_clock::now();
    duration = duration_cast<microseconds>(stop - start);
    cout << "Bit Vector Dijkstra: " << duration.count() << " microseconds\n\n";

    // Block 4: Топологическая сортировка
    cout << "Block 4: Topological Sort\n";

    start = high_resolution_clock::now();
    topologicalSortMatrix(matrixGraph);
    stop = high_resolution_clock::now();
    duration = duration_cast<microseconds>(stop - start);
    cout << "Matrix Topological Sort: " << duration.count() << " microseconds\n\n";

    start = high_resolution_clock::now();
    topologicalSortBitVector(bitVectorGraph);
    stop = high_resolution_clock::now();
    duration = duration_cast<microseconds>(stop - start);
    cout << "Bit Vector Topological Sort: " << duration.count() << " microseconds\n\n";

    // Block 5: Минимальное остовное дерево (на основе BFS)
    cout << "Block 5: Minimum Spanning Tree (BFS)\n";

    start = high_resolution_clock::now();
    BFSForMSTMatrix(matrixGraph, 0);
    stop = high_resolution_clock::now();
    duration = duration_cast<microseconds>(stop - start);
    cout << "Matrix MST using BFS: " << duration.count() << " microseconds\n\n";

    start = high_resolution_clock::now();
    BFSForMSTBitVector(bitVectorGraph, 0);
    stop = high_resolution_clock::now();
    duration = duration_cast<microseconds>(stop - start);
    cout << "Bit Vector MST using BFS: " << duration.count() << " microseconds\n\n";

    // Block 6: Алгоритм Краскала
    cout << "Block 6: Kruskal's Algorithm\n";

    start = high_resolution_clock::now();
    KruskalMST(kruskalGraph);
    stop = high_resolution_clock::now();
    duration = duration_cast<microseconds>(stop - start);
    cout << "Kruskal's MST: " << duration.count() << " microseconds\n\n";

    cout << "Benchmark mode completed.\n";
}




void addEdgeMatrix(GraphMatrix& graph, int src, int dest, int weight, bool directed) {
    graph.adjMatrix[src][dest] = weight;
    if (!directed) {
        graph.adjMatrix[dest][src] = weight;
    }
}

void printGraphMatrix(const GraphMatrix& graph) {
    for (int i = 0; i < graph.numVertices; ++i) {
        for (int j = 0; j < graph.numVertices; ++j) {
            if (graph.adjMatrix[i][j] == INF) {
                cout << "INF ";
            } else {
                cout << graph.adjMatrix[i][j] << " ";
            }
        }
        cout << endl;
    }
}

void addEdgeBitVector(GraphBitVector& graph, int src, int dest, bool directed) {
    graph.adjBitVector[src].set(dest);
    if (!directed) {
        graph.adjBitVector[dest].set(src);
    }
}

void printGraphBitVector(const GraphBitVector& graph) {
    for (int i = 0; i < graph.numVertices; ++i) {
        cout << "Vertex " << i << ": " << graph.adjBitVector[i] << endl;
    }
}

void generateRandomGraphMatrix(GraphMatrix& graph, int numEdges, bool directed) {
    srand(time(0));
    set<pair<int, int>> edges;
    while (edges.size() < numEdges) {
        int src = rand() % graph.numVertices;
        int dest = rand() % graph.numVertices;
        if (src != dest && edges.find({src, dest}) == edges.end()) {
            int weight = rand() % 10 + 1;
            addEdgeMatrix(graph, src, dest, weight, directed);
            edges.insert({src, dest});
            if (!directed) {
                edges.insert({dest, src});
            }
        }
    }
}

void generateRandomGraphBitVector(GraphBitVector& graph, int numEdges, bool directed) {
    srand(time(0));
    set<pair<int, int>> edges;
    while (edges.size() < numEdges) {
        int src = rand() % graph.numVertices;
        int dest = rand() % graph.numVertices;
        if (src != dest && edges.find({src, dest}) == edges.end()) {
            addEdgeBitVector(graph, src, dest, directed);
            edges.insert({src, dest});
            if (!directed) {
                edges.insert({dest, src});
            }
        }
    }
}

GraphBitVector convertMatrixToBitVector(const GraphMatrix& matrixGraph) {
    GraphBitVector bitVectorGraph(matrixGraph.numVertices);
    for (int i = 0; i < matrixGraph.numVertices; ++i) {
        for (int j = 0; j < matrixGraph.numVertices; ++j) {
            if (matrixGraph.adjMatrix[i][j] != INF && matrixGraph.adjMatrix[i][j] != 0) {
                addEdgeBitVector(bitVectorGraph, i, j, false); // Assuming undirected for simplicity
            }
        }
    }
    return bitVectorGraph;
}

GraphMatrix convertBitVectorToMatrix(const GraphBitVector& bitVectorGraph) {
    GraphMatrix matrixGraph(bitVectorGraph.numVertices);
    for (int i = 0; i < bitVectorGraph.numVertices; ++i) {
        for (int j = 0; j < bitVectorGraph.numVertices; ++j) {
            if (bitVectorGraph.adjBitVector[i][j]) {
                addEdgeMatrix(matrixGraph, i, j, 1, false); // Assuming weight of 1 for simplicity
            }
        }
    }
    return matrixGraph;
}

void DFSMatrixUtil(const GraphMatrix& graph, int vertex, vector<bool>& visited) {
    visited[vertex] = true;
    cout << vertex << " ";
    for (int i = 0; i < graph.numVertices; ++i) {
        if (graph.adjMatrix[vertex][i] != INF && !visited[i]) {
            DFSMatrixUtil(graph, i, visited);
        }
    }
}

void DFSMatrix(const GraphMatrix& graph, int startVertex) {
    vector<bool> visited(graph.numVertices, false);
    DFSMatrixUtil(graph, startVertex, visited);
    cout << endl;
}

void DFSBitVectorUtil(const GraphBitVector& graph, int vertex, vector<bool>& visited) {
    visited[vertex] = true;
    cout << vertex << " ";
    for (int i = 0; i < graph.numVertices; ++i) {
        if (graph.adjBitVector[vertex][i] && !visited[i]) {
            DFSBitVectorUtil(graph, i, visited);
        }
    }
}

void DFSBitVector(const GraphBitVector& graph, int startVertex) {
    vector<bool> visited(graph.numVertices, false);
    DFSBitVectorUtil(graph, startVertex, visited);
    cout << endl;
}

void dijkstraMatrix(const GraphMatrix& graph, int startVertex) {
    vector<int> dist(graph.numVertices, INF);
    vector<bool> sptSet(graph.numVertices, false);
    dist[startVertex] = 0;

    for (int count = 0; count < graph.numVertices - 1; ++count) {
        int min = INF, minIndex;
        for (int v = 0; v < graph.numVertices; ++v)
            if (!sptSet[v] && dist[v] <= min)
                min = dist[v], minIndex = v;

        int u = minIndex;
        sptSet[u] = true;

        for (int v = 0; v < graph.numVertices; ++v)
            if (!sptSet[v] && graph.adjMatrix[u][v] != INF && dist[u] != INF && dist[u] + graph.adjMatrix[u][v] < dist[v])
                dist[v] = dist[u] + graph.adjMatrix[u][v];
    }

    cout << "Vertex Distance from Source\n";
    for (int i = 0; i < graph.numVertices; ++i)
        if (dist[i] == INF)
            cout << i << " \t\t " << "INF" << "\n";
        else
            cout << i << " \t\t " << dist[i] << "\n";
}

void dijkstraBitVector(const GraphBitVector& graph, int startVertex) {
    vector<int> dist(graph.numVertices, INF);
    vector<bool> sptSet(graph.numVertices, false);
    dist[startVertex] = 0;

    for (int count = 0; count < graph.numVertices - 1; ++count) {
        int min = INF, minIndex;
        for (int v = 0; v < graph.numVertices; ++v)
            if (!sptSet[v] && dist[v] <= min)
                min = dist[v], minIndex = v;

        int u = minIndex;
        sptSet[u] = true;

        for (int v = 0; v < graph.numVertices; ++v)
            if (!sptSet[v] && graph.adjBitVector[u][v] && dist[u] != INF && dist[u] + 1 < dist[v])
                dist[v] = dist[u] + 1;
    }

    cout << "Vertex Distance from Source\n";
    for (int i = 0; i < graph.numVertices; ++i)
        if (dist[i] == INF)
            cout << i << " \t\t " << "INF" << "\n";
        else
            cout << i << " \t\t " << dist[i] << "\n";
}

void topologicalSortUtilMatrix(const GraphMatrix& graph, int v, vector<bool>& visited, stack<int>& Stack) {
    visited[v] = true;
    for (int i = 0; i < graph.numVertices; ++i) {
        if (graph.adjMatrix[v][i] != INF && !visited[i]) {
            topologicalSortUtilMatrix(graph, i, visited, Stack);
        }
    }
    Stack.push(v);
}

void topologicalSortMatrix(const GraphMatrix& graph) {
    stack<int> Stack;
    vector<bool> visited(graph.numVertices, false);

    for (int i = 0; i < graph.numVertices; ++i) {
        if (!visited[i]) {
            topologicalSortUtilMatrix(graph, i, visited, Stack);
        }
    }

    while (!Stack.empty()) {
        cout << Stack.top() << " ";
        Stack.pop();
    }
    cout << endl;
}

void topologicalSortUtilBitVector(const GraphBitVector& graph, int v, vector<bool>& visited, stack<int>& Stack) {
    visited[v] = true;
    for (int i = 0; i < graph.numVertices; ++i) {
        if (graph.adjBitVector[v][i] && !visited[i]) {
            topologicalSortUtilBitVector(graph, i, visited, Stack);
        }
    }
    Stack.push(v);
}

void topologicalSortBitVector(const GraphBitVector& graph) {
    stack<int> Stack;
    vector<bool> visited(graph.numVertices, false);

    for (int i = 0; i < graph.numVertices; ++i) {
        if (!visited[i]) {
            topologicalSortUtilBitVector(graph, i, visited, Stack);
        }
    }

    while (!Stack.empty()) {
        cout << Stack.top() << " ";
        Stack.pop();
    }
    cout << endl;
}

void BFSMatrix(const GraphMatrix& graph, int startVertex) {
    vector<bool> visited(graph.numVertices, false);
    queue<int> q;
    q.push(startVertex);
    visited[startVertex] = true;

    while (!q.empty()) {
        int vertex = q.front();
        cout << vertex << " ";
        q.pop();

        for (int i = 0; i < graph.numVertices; ++i) {
            if (graph.adjMatrix[vertex][i] != INF && !visited[i]) {
                q.push(i);
                visited[i] = true;
            }
        }
    }
    cout << endl;
}

void BFSBitVector(const GraphBitVector& graph, int startVertex) {
    vector<bool> visited(graph.numVertices, false);
    queue<int> q;
    q.push(startVertex);
    visited[startVertex] = true;

    while (!q.empty()) {
        int vertex = q.front();
        cout << vertex << " ";
        q.pop();

        for (int i = 0; i < graph.numVertices; ++i) {
            if (graph.adjBitVector[vertex][i] && !visited[i]) {
                q.push(i);
                visited[i] = true;
            }
        }
    }
    cout << endl;
}

Graph createGraph(int V, int E) {
    Graph graph;
    graph.V = V;
    graph.E = E;
    return graph;
}

int find(vector<int>& parent, int i) {
    if (parent[i] == i)
        return i;
    return find(parent, parent[i]);
}

void Union(vector<int>& parent, vector<int>& rank, int x, int y) {
    int xroot = find(parent, x);
    int yroot = find(parent, y);

    if (rank[xroot] < rank[yroot])
        parent[xroot] = yroot;
    else if (rank[xroot] > rank[yroot])
        parent[yroot] = xroot;
    else {
        parent[yroot] = xroot;
        rank[xroot]++;
    }
}

void KruskalMST(Graph& graph) {
    vector<Edge> result(graph.V - 1); // исправлено
    int e = 0;
    int i = 0;

    sort(graph.edges.begin(), graph.edges.end(),
         [](Edge a, Edge b) { return a.weight < b.weight; });

    vector<int> parent(graph.V);
    vector<int> rank(graph.V, 0);

    for (int v = 0; v < graph.V; ++v)
        parent[v] = v;

    while (e < graph.V - 1 && i < graph.edges.size()) {
        Edge next_edge = graph.edges[i++];

        int x = find(parent, next_edge.src);
        int y = find(parent, next_edge.dest);

        if (x != y) {
            result[e++] = next_edge;
            Union(parent, rank, x, y);
        }
    }

    cout << "Following are the edges in the constructed MST\n";
    int minimumCost = 0;
    for (i = 0; i < e; ++i) {
        cout << result[i].src << " -- " << result[i].dest << " == " << result[i].weight << endl;
        minimumCost += result[i].weight;
    }
    cout << "Minimum Cost Spanning Tree: " << minimumCost << endl;
}

void addEdgeKruskal(Graph& graph, int src, int dest, int weight) {
    Edge edge = {src, dest, weight};
    graph.edges.push_back(edge);
}

bool isConnectedMatrixUtil(const GraphMatrix& graph, int vertex, vector<bool>& visited) {
    visited[vertex] = true;
    for (int i = 0; i < graph.numVertices; ++i) {
        if (graph.adjMatrix[vertex][i] != INF && !visited[i]) {
            isConnectedMatrixUtil(graph, i, visited);
        }
    }
    for (bool v : visited) {
        if (!v) return false;
    }
    return true;
}

bool isConnectedMatrix(const GraphMatrix& graph) {
    vector<bool> visited(graph.numVertices, false);
    return isConnectedMatrixUtil(graph, 0, visited);
}

bool isConnectedBitVectorUtil(const GraphBitVector& graph, int vertex, vector<bool>& visited) {
    visited[vertex] = true;
    for (int i = 0; i < graph.numVertices; ++i) {
        if (graph.adjBitVector[vertex][i] && !visited[i]) {
            isConnectedBitVectorUtil(graph, i, visited);
        }
    }
    for (bool v : visited) {
        if (!v) return false;
    }
    return true;
}

bool isConnectedBitVector(const GraphBitVector& graph) {
    vector<bool> visited(graph.numVertices, false);
    return isConnectedBitVectorUtil(graph, 0, visited);
}

void BFSForMSTMatrix(const GraphMatrix& graph, int startVertex) {
    vector<bool> visited(graph.numVertices, false);
    queue<int> q;
    vector<int> mst;
    q.push(startVertex);
    visited[startVertex] = true;

    while (!q.empty()) {
        int vertex = q.front();
        mst.push_back(vertex);
        q.pop();

        for (int i = 0; i < graph.numVertices; ++i) {
            if (graph.adjMatrix[vertex][i] != INF && !visited[i]) {
                q.push(i);
                visited[i] = true;
            }
        }
    }

    cout << "MST using BFS:\n";
    for (int v : mst) {
        cout << v << " ";
    }
    cout << endl;
}

void BFSForMSTBitVector(const GraphBitVector& graph, int startVertex) {
    vector<bool> visited(graph.numVertices, false);
    queue<int> q;
    vector<int> mst;
    q.push(startVertex);
    visited[startVertex] = true;

    while (!q.empty()) {
        int vertex = q.front();
        mst.push_back(vertex);
        q.pop();

        for (int i = 0; i < graph.numVertices; ++i) {
            if (graph.adjBitVector[vertex][i] && !visited[i]) {
                q.push(i);
                visited[i] = true;
            }
        }
    }

    cout << "MST using BFS:\n";
    for (int v : mst) {
        cout << v << " ";
    }
    cout << endl;
}
