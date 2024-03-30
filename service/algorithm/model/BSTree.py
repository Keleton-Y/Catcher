from algorithm.model.SCTask import *
import pickle


class BSTNode(object):
    def __init__(self, task_obj, tid, parent=None):
        # Key of this node (used for BST sorting, content is the score between the task and the cache worker)
        self.key = task_obj.score[tid]
        # Object stored in this node
        self.task = task_obj
        # Left child node
        self.left = None
        # Right child node
        self.right = None
        # Parent node
        self.parent = parent
        # Size of subtree
        self.size = 1

    # Test print function
    def printNode(self):
        print('---', self.key, '---')


class BSTree(object):
    def __init__(self, tid, task_list=None):
        # tid is equivalent to the worker's id
        self.id = tid
        self.root = None
        # If task_list is not None, it means initializing the search tree with this list
        if task_list is not None:
            self.buildTree(task_list)

    # Build a binary search tree based on a sorted array (ascending order)
    def buildTree(self, task_list):
        left = 0
        right = len(task_list) - 1
        mid = int((left + right) / 2)
        self.root = BSTNode(task_list[mid], self.id)
        self.root.size = right - left + 1
        if left < mid:
            self.root.left = self._build(task_list, left, mid-1, self.root)
        if right > mid:
            self.root.right = self._build(task_list, mid+1, right, self.root)

    def _build(self, task_list, left, right, parent=None):
        mid = int((left + right) / 2)
        ret = BSTNode(task_list[mid], self.id, parent)
        ret.size = right - left + 1
        if left < mid:
            ret.left = self._build(task_list, left, mid-1, ret)
        if right > mid:
            ret.right = self._build(task_list, mid+1, right, ret)
        return ret

    def insert(self, key, task):
        # Insert a task into the tree, where key is the task's score
        # If the root node exists, continue recursive search; otherwise, create a root node
        if self.root is not None:
            self._insert(key, task, self.root)
        else:
            self.root = BSTNode(task, self.id)

    def _insert(self, key, task, curNode):
        # According to the properties of BST: all nodes in the left subtree are smaller than itself, and all nodes in the right subtree are larger than itself, perform recursive insertion
        # Since it must be inserted into the subtree of curNode, increase size by one
        curNode.size += 1
        if key < curNode.key:
            if curNode.left is not None:
                self._insert(key, task, curNode.left)
            else:
                curNode.left = BSTNode(task, self.id, parent=curNode)
        else:
            if curNode.right is not None:
                self._insert(key, task, curNode.right)
            else:
                curNode.right = BSTNode(task, self.id, parent=curNode)

    def find(self, key):
        # Find a task based on the given key (score)
        res = None
        if self.root is not None:
            res = self._find(key, self.root)
        # No handling for the case where res is None, assuming all nodes can be found by default
        return res

    def _find(self, key, curNode):
        # Recursively search according to the structure
        if curNode is None:
            return None
        elif abs(curNode.key - key) <= 1e-8:
            return curNode
        elif key < curNode.key:
            return self._find(key, curNode.left)
        else:
            return self._find(key, curNode.right)

    def find_kth(self, k):
        return self._find_kth(k, self.root)

    def _find_kth(self, k, curNode):
        # Find the object based on the given rank (kth, i.e., smaller than k-1 nodes in terms of key)
        # The right subtree may be empty, so calculate the number of nodes larger than the current node
        largerCnt = 0
        if curNode.right is not None:
            largerCnt = curNode.right.size
        # If the sum of the right subtree and the current node's number is less than k, the target node is in the left subtree
        if k > largerCnt + 1:
            return self._find_kth(k-largerCnt-1, curNode.left)
        elif k == largerCnt + 1:
            return curNode
        else:
            return self._find_kth(k, curNode.right)

    def delete(self, key):
        # Delete the corresponding node in the tree based on the given key
        delNode = self.find(key)
        # Delete node, using lazy deletion, so the actual efficiency may be low (when the tree has been used for a long time)
        delNode.task = None
        self._delete(delNode)

    def delete_kth(self, k):
        # Delete the corresponding node in the tree based on the given rank; as it is used to adjust the cache size, this function needs to return the deleted task
        delNode = self.find_kth(k)
        delTask = delNode.task
        # Delete node, using lazy deletion, so the actual efficiency may be low (when the tree has been used for a long time)
        delNode.task = None
        self._delete(delNode)

    def _delete(self, node):
        # Handle the effects of deleting this node
        node.size -= 1
        if node.parent is not None:
            self._delete(node.parent)

    # In-order traversal for testing
    def leftFirstSearch(self):
        self._LFS(self.root)

    def _LFS(self, curNode):
        if curNode is None:
            return
        self._LFS(curNode.left)
        if curNode.task is not None:
            curNode.printNode()
        self._LFS(curNode.right)

    # Right-root-left order traversal, can get tasks arranged in descending order of scores
    def rightFirstSearch(self):
        self._RFS(self.root)

    def _RFS(self, curNode):
        if curNode is None:
            return
        self._RFS(curNode.right)
        if curNode.task is not None:
            curNode.printNode()
        self._RFS(curNode.left)



if __name__ == '__main__':
    loadStart = time.perf_counter()
    with open('..\\..\\data\\TaskList_CD_20161101.dat', 'rb') as file:
        tasks = pickle.load(file)
    print('加载用时', time.perf_counter() - loadStart)

    '''
    task1 = tasks[0]
    task2 = tasks[1]
    task3 = tasks[2]
    task1.score[100] = 1
    task2.score[100] = 15
    task3.score[100] = 5.5
    testTree.insert(1, task1)
    testTree.insert(15, task2)
    testTree.insert(5.5, task3)
    '''
    taskList = []
    for i in range(100):
        tTask = tasks[i]
        tTask.score[100] = i
        taskList.append(tTask)
    '''
    testTree.find(1).printNode()
    testTree.find(15).printNode()
    testTree.find(5.5).printNode()
    '''
    testTree = BSTree(100, taskList)
    testTree.delete_kth(12)
    testTree.leftFirstSearch()
    '''
    print(testTree.find_kth(2).task.score[100])
    print(testTree.find_kth(1).task.score[100])
    print(testTree.find_kth(3).task.score[100])
    '''
    pass
