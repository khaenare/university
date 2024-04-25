/*
Блок 0: 1             done
Блок 1: 2, 3          done
Блок 2: 7             done
Блок 3: 13, 15        done
Блок 4: 18            done
Блок 5: 21            done
Блок 6: 26            done???????
*/

#include <iostream>
#include <vector>
#include <string>
#include <cmath>
#include <map>
#include <stack>
#include <cctype>
#include <sstream>

using namespace std;

//Блок 0
struct TreeNode {
    int data;
    vector<TreeNode*> children;

    TreeNode(int value) : data(value) {}
};                                                                //№1
void addChild(TreeNode* parent, int childData);                                       //№1
void deleteTree(TreeNode* node);                                                      //№1
//Блок 1
TreeNode* getNode(TreeNode* root, const vector<int>& path);                           //№2
bool getPath(TreeNode* root, int value, vector<int>& path);                           //№2
void addNode(TreeNode* root, const vector<int>& path, int value);                     //№3
vector<int> parsePath(const string& input);
//Блок 2
void printTree(TreeNode* node, string prefix = "");                                   //№7
//Блок 3
TreeNode* removeNodeByPath(TreeNode* root, const vector<int>& path);                  //№13
void removeNodesByValue(TreeNode* &node, int value, vector<TreeNode*> &toDelete);     //№15
void deleteNodesWithValue(TreeNode* &root, int value);                                //№15
//Блок 4
struct BinaryTreeNode {
    int data;
    BinaryTreeNode* left;
    BinaryTreeNode* right;

    BinaryTreeNode(int value) : data(value), left(nullptr), right(nullptr) {}
};                                                          //№18
void insert(BinaryTreeNode*& node, int value);                                        //№18
void printBinaryTree(BinaryTreeNode* node, string prefix = "");                       //№18
//Блок 5
void preorderTraversal(BinaryTreeNode* node, vector<int>& result);                    //№21
//Блок 6                                                                              //№22
struct ExpressionNode {
    string value;
    ExpressionNode* left;
    ExpressionNode* right;

    ExpressionNode(const string& val) : value(val), left(nullptr), right(nullptr) {}
};
bool isOperator(const string& token);
bool isVariable(const string& token);
bool isNumeric(const string& token);
double evaluate(ExpressionNode* root, const map<string, double>& variables);
ExpressionNode* simplify(ExpressionNode* root, const map<string, double>& variables);
ExpressionNode* constructExpressionTree(const string& expression);
void printInfix(ExpressionNode* root, bool isRoot = true);




void interactiveMode();
void demonstrationMode();





int main() {
    int mode;
    cout << "Select mode:\n1. Interactive mode \n2. Demonstration mode:\nEnter a number of mode: ";
    cin >> mode;

    switch (mode) {
        case 1:
            interactiveMode();
            break;
        case 2:
            demonstrationMode();
            break;
        default:
            cerr << "Error! You enter incorrect mode\n";
            break;
    }
    return 0;
}




void interactiveMode() {
    TreeNode* root = nullptr;
    ExpressionNode* exprTree = nullptr;
    BinaryTreeNode* binTree = nullptr;
    vector<int> traversalResult;

    int option;
    int mode;
    int value;
    string input;
    string expression;
    vector<int> path;
    do {
        cout << "Select mode:\n1. Tree \n2. Binary Tree\n3. Expression Tree\n4. Exit \nEnter a number of mode: ";
        cin >> mode;

        switch (mode) {
            case 1:
                cout << "Select operation:\n1. Add node to the tree \n2. Add  node by path \n 3. Remove node by value from the tree\n4. Remove node by path\n5. Print the tree\nEnter a number of operation: ";
                cin >> option;
                switch (option) {
                    case 1:
                        cout << "Enter value of the node to add: ";
                        cin >> value;
                        addChild(root, value);
                        break;
                    case 2:
                        cout << "Enter value of the node to add: ";
                        cin >> value;
                        cout << "Enter path to node (fe: 0 1 0 1 1): ";
                        cin.ignore();
                        getline(cin, input);
                        path = parsePath(input);
                        addNode(root, path, value);
                        break;
                    case 3:
                        cout << "Enter value of the node to remove: ";
                        cin >> value;
                        deleteNodesWithValue(root, value);
                        break;
                    case 4:
                        cout << "Enter path to node (fe: 0 1 0 1 1): ";
                        cin.ignore();
                        getline(cin, input);
                        path = parsePath(input);
                        removeNodeByPath(root, path);
                        break;
                    case 5:
                        cout << "The tree:\n";
                        printTree(root);
                        break;
                    default:
                        cerr << "Error! You enter incorrect operation\n";
                        break;}
                break;
            case 2:
                cout << "Select operation:\n1. Insert value \n2. Print Tree\n3. Perform preorder traversal\nEnter a number of operation: ";
                cin >> option;
                switch (option) {
                    case 1:
                        int value;
                        cout << "Enter value to insert into binary tree: ";
                        cin >> value;
                        insert(binTree, value);
                        break;
                    case 2:
                        cout << "Binary tree:\n";
                        printBinaryTree(binTree, "");
                        break;
                    case 3:
                        cout << "Preorder traversal result:\n";
                        traversalResult.clear();
                        preorderTraversal(binTree, traversalResult);
                        for (int value : traversalResult) {
                            cout << value << " ";
                        }
                        cout << endl;
                        break;
                    default:
                        cerr << "Error! You enter incorrect operation\n";
                        break;}
                break;
            case 3:
                cout << "Select operation:\n1. Create expression tree \n2. Print Infix Expression\nEnter a number of operation: ";
                cin >> option;
                switch (option) {
                    case 1:
                        cout << "Enter an expression in postfix notation: ";
                        cin.ignore();
                        getline(cin, expression);
                        exprTree = constructExpressionTree(expression);
                        cout << "Expression tree created" << endl;
                        break;
                    case 2:
                        if (exprTree != nullptr) {
                            cout << "Infix Expression: ";
                            printInfix(exprTree);
                            cout << endl;
                        } else {
                            cout << "Expression tree isn`t created" << endl;
                        }
                        break;
                    default:
                        cerr << "Error! You enter incorrect operation\n";
                        break;}
                break;
            case 4:
                cout << "Exiting...\n";
                break;
            default:
                cerr << "Error! You enter incorrect mode\n";
                break;
        }
    } while (option != 9);
}

void demonstrationMode() {

    TreeNode* rooot = new TreeNode(1);
    addChild(rooot, 2);
    addChild(rooot, 3);
    addChild(rooot->children[0], 4);
    addChild(rooot->children[0], 5);
    addChild(rooot->children[1], 6);
    cout << "\nPrint of the ordinary tree: ";
    printTree(rooot);

    BinaryTreeNode* binaryTreeRoot = nullptr;
    insert(binaryTreeRoot, 10);
    insert(binaryTreeRoot, 5);
    insert(binaryTreeRoot, 15);
    insert(binaryTreeRoot, 3);
    insert(binaryTreeRoot, 8);

    vector<int> result;
    cout << "\n\nPreorder traversal of binary tree: ";
    preorderTraversal(binaryTreeRoot, result);
    for (int value : result) {
        cout << value << " ";
    }
    cout << endl;

    cout << "\nMax-Min binary tree: \n";
    printBinaryTree(binaryTreeRoot, "");

    ExpressionNode* root = new ExpressionNode("*");
    root->left = new ExpressionNode("+");
    root->right = new ExpressionNode("y");
    root->left->left = new ExpressionNode("x");
    root->left->right = new ExpressionNode("2");

    cout << "\nOriginal expression converted to infix form: ";
    printInfix(root);
    cout << endl;

    map<string, double> variables = {{"x", 2.5}, {"y", 1.5}};
    ExpressionNode* simplifiedRoot = simplify(root, variables);
    cout << "Simplified expression with fixed variables (x = 2.5 and y = 1.5): ";
    printInfix(simplifiedRoot);
    cout << endl;
}




void addChild(TreeNode* parent, int childData) {
    TreeNode* child = new TreeNode(childData);
    parent->children.push_back(child);
}
void deleteTree(TreeNode* node) {
    for (TreeNode* child : node->children) {
        deleteTree(child);
    }
    delete node;
}
TreeNode* getNode(TreeNode* root, const vector<int>& path) {
    TreeNode* current = root;
    for (int index : path) {
        if (index < 0 || index >= current->children.size()) {
            return nullptr;
        }
        current = current->children[index];
    }
    return current;
}
bool getPath(TreeNode* root, int value, vector<int>& path) {
    if (root->data == value) {
        return true;
    }

    for (int i = 0; i < root->children.size(); i++) {
        path.push_back(i);
        if (getPath(root->children[i], value, path)) {
            return true;
        }
        path.pop_back();
    }

    return false;
}
void addNode(TreeNode* root, const vector<int>& path, int value) {
    TreeNode* parent = getNode(root, path);
    if (parent != nullptr) {
        addChild(parent, value);
    } else {
        cout << "Incorrect path" << endl;
    }
}
void printTree(TreeNode* node, string prefix) {
    if (!node) return;

    cout << prefix << node->data;
    if (!node->children.empty()) {
        cout << " (";
        for (int i = 0; i < node->children.size(); ++i) {
            printTree(node->children[i], "");
            if (i < node->children.size() - 1) cout << ", ";
        }
        cout << ")";
    }
}
TreeNode* removeNodeByPath(TreeNode* root, const vector<int>& path) {
    if (path.empty()) return nullptr;

    TreeNode* parent = root;
    for (int i = 0; i < path.size() - 1; ++i) {
        if (path[i] < 0 || path[i] >= parent->children.size()) {
            return nullptr;
        }
        parent = parent->children[path[i]];
    }

    int indexToRemove = path.back();
    if (indexToRemove < 0 || indexToRemove >= parent->children.size()) {
        return nullptr;
    }

    TreeNode* nodeToRemove = parent->children[indexToRemove];
    parent->children.erase(parent->children.begin() + indexToRemove);
    return nodeToRemove;
}
void removeNodesByValue(TreeNode* &node, int value, vector<TreeNode*> &toDelete) {
    for (auto it = node->children.begin(); it != node->children.end(); ) {
        if ((*it)->data == value) {
            removeNodesByValue(*it, value, toDelete);
            delete *it;
            it = node->children.erase(it);
        } else {
            removeNodesByValue(*it, value, toDelete);
            ++it;
        }
    }
}
void deleteNodesWithValue(TreeNode* &root, int value) {
    vector<TreeNode*> toDelete;
    if (root->data == value) {
        removeNodesByValue(root, value, toDelete);
        delete root;
        root = nullptr;
    } else {
        removeNodesByValue(root, value, toDelete);
    }
}
void insert(BinaryTreeNode*& node, int value) {
    if (!node) {
        node = new BinaryTreeNode(value);
    } else if (value < node->data) {
        insert(node->left, value);
    } else {
        insert(node->right, value);
    }
}
void printBinaryTree(BinaryTreeNode* node, string prefix) {
    if (!node) return;

    cout << prefix << node->data << "\n";
    if (node->left) printBinaryTree(node->left, prefix + "Left: ");
    if (node->right) printBinaryTree(node->right, prefix + "Right: ");
}
void preorderTraversal(BinaryTreeNode* node, vector<int>& result) {
    if (!node) return;

    result.push_back(node->data);
    preorderTraversal(node->left, result);
    preorderTraversal(node->right, result);
}
bool isOperator(const string& token) {
    return token == "+" || token == "-" || token == "*" || token == "/" || token == "^";
}
bool isVariable(const string& token) {
    return isalpha(token[0]);
}
bool isNumeric(const string& token) {
    for (char c : token) {
        if (!isdigit(c) && c != '.') {
            return false;
        }
    }
    return true;
}
double evaluate(ExpressionNode* root, const map<string, double>& variables) {
    if (root == nullptr) return 0.0;

    if (!isOperator(root->value)) {
        if (isdigit(root->value[0]) || root->value[0] == '-') {
            return stod(root->value);
        } else {
            auto it = variables.find(root->value);
            if (it != variables.end()) {
                return it->second;
            } else {
                cerr << "Error in " << root->value  << endl;
                return 0.0;
            }
        }
    }

    double leftValue = evaluate(root->left, variables);
    double rightValue = evaluate(root->right, variables);

    if (root->value == "+") {
        return leftValue + rightValue;
    } else if (root->value == "-") {
        return leftValue - rightValue;
    } else if (root->value == "*") {
        return leftValue * rightValue;
    } else if (root->value == "/") {
        if (rightValue == 0) {
            cerr << "Division by zero" << endl;
            return 0.0;
        }
        return leftValue / rightValue;
    } else if (root->value == "^") {
        return pow(leftValue, rightValue);
    }

    cerr << "Error in " << root->value << endl;
    return 0.0;
}
ExpressionNode* simplify(ExpressionNode* root, const map<string, double>& variables) {
    if (root == nullptr) return nullptr;

    if (!isOperator(root->value)) {
        if (variables.find(root->value) != variables.end()) {
            return new ExpressionNode(to_string(variables.at(root->value)));
        } else {
            return new ExpressionNode(root->value);
        }
    }

    ExpressionNode* left = simplify(root->left, variables);
    ExpressionNode* right = simplify(root->right, variables);

    if (!isOperator(left->value) && !isOperator(right->value)) {
        double result = evaluate(root, variables);
        return new ExpressionNode(to_string(result));
    }

    root->left = left;
    root->right = right;
    return root;
}
ExpressionNode* constructExpressionTree(const string& expression) {
    stack<ExpressionNode*> nodeStack;

    for (char current : expression) {
        if (isspace(current)) {
            continue;
        }

        if (isalnum(current)) {
            nodeStack.push(new ExpressionNode(string(1, current)));
        } else {
            ExpressionNode* rightOperand = nodeStack.top();
            nodeStack.pop();
            ExpressionNode* leftOperand = nodeStack.top();
            nodeStack.pop();

            ExpressionNode* operatorNode = new ExpressionNode(string(1, current));
            operatorNode->left = leftOperand;
            operatorNode->right = rightOperand;

            nodeStack.push(operatorNode);
        }
    }

    return nodeStack.top();
}
void printInfix(ExpressionNode* root, bool isRoot) {
    if (root == nullptr) return;

    if (!isRoot && isOperator(root->value)) {
        cout << "(";
    }

    printInfix(root->left, false);
    cout << root->value;
    printInfix(root->right, false);

    if (!isRoot && isOperator(root->value)) {
        cout << ")";
    }
}
vector<int> parsePath(const string& input) {
    vector<int> path;
    stringstream ss(input);
    int num;
    while (ss >> num) {
        path.push_back(num);
    }
    return path;
}
