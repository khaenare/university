/*
Блок 0: 1             done
Блок 1: 2, 3          done
Блок 2: 7             done
Блок 3: 13, 15        done
Блок 4: 18            done
Блок 5: 21
Блок 6: 22
*/

#include <iostream>
#include <vector>
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






int main() {
    TreeNode* root = new TreeNode(1);
    
    addChild(root, 2);
    addChild(root, 3);
    
    addChild(root->children[0], 4);
    addChild(root->children[0], 5);
    addChild(root->children[1], 6);
    
    printTree(root);
    
    
    

    BinaryTreeNode* rooot = nullptr;
    
    insert(rooot, 10);
    insert(rooot, 5);
    insert(rooot, 15);
    insert(rooot, 3);
    insert(rooot, 7);
    insert(rooot, 12);
    insert(rooot, 18);
    
    printBinaryTree(rooot);

    return 0;
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
