import queue
import random

from algorithm.model.BSTree import *
from algorithm.model.SCTask import *
from algorithm.utils.Constants import *
import time
import pickle

init_cnt = 0


# Task buffer for each worker's TopK cache structure
class TaskBuffer(object):
    def __init__(self, bid):
        # Cache ID is the same as the worker's ID
        self.id = bid
        # The second-level cache is a binary search tree; the capacity is initially three times K, and there is also a threshold table in the structure of the second-level cache
        # It should be noted that Top-K is obtained by traversing L2 in the right-root-left order to get the top k results
        self.L2 = BSTree(self.id)
        self.cacheSize = TOP_K * 3
        # Threshold table, used to analyze the current best threshold
        self.thresholdList = []
        self._initTL()
        # Threshold, only tasks with scores greater than or equal to this value can safely enter L2 cache
        self.threshold = 0
        # First-level cache, storing all tasks that can be picked up by workers
        self.L1 = []
        # Structure used by the baseline method
        self.skyband = []
        self.topK = []

    def initL1(self, baseTasks):
        # Initialize after the worker appears; baseTasks contains tasks that have passed the constraint check
        self.L1 = baseTasks

    def initL2(self):
        # Use a min heap to get the first cacheSize tasks
        minHeap = queue.PriorityQueue()
        for task in self.L1:
            try:
                minHeap.put([task.score[self.id]+random.random()*0.00001, task])
                if minHeap.qsize() > self.cacheSize:
                    minHeap.get()
            except TypeError:
                pass
        # Put into L2: first create a temporary array and initialize the search tree on this array
        taskList = []
        # At this time, minHeap contains all tasks with scores as the top cacheSize
        # It should be noted that the structure stored in minHeap is [score, task], and only the task needs to be taken at this time
        while minHeap.qsize():
            taskList.append(minHeap.get()[1])
        self.L2 = BSTree(self.id, taskList)

    def refresh(self):
        self.L1 = []
        self.L2 = BSTree(self.id)
        if random.randint(1, 5) == 1:
            time.sleep(1 / 1000)

    def _initTL(self):
        # TL --> Threshold List
        # Initialize the threshold table and insert a special task with a score of -1 and an end time of INF into it
        guardTask = taskModel(None, 100000000000, None, None)
        guardTask.score[self.id] = -1
        self.thresholdList.append(guardTask)

    def addTask(self, task):
        # Calling this function indicates that the task satisfies the constraint with the worker, at least it can be added to L1
        # 1. Add to L1
        self.L1.append(task)
        # 2. Add to L2, determine whether to insert the task by the insertL2 function
        self._insertL2(task)

    def _insertL2(self, task):
        # Determine whether it exceeds the threshold, and do not insert if it does not exceed
        key = task.score[self.id]
        if key < self.threshold:
            return
        # Call the insert function of the binary search tree
        self.L2.insert(key, task)
        # If the quantity exceeds the upper limit, the last one needs to be deleted
        if self.L2.root.size > self.cacheSize:
            delTask = self.L2.find_kth(self.cacheSize + 1).task
            if delTask is None:
                return
            self.threshold = max(self.threshold, delTask.score[self.id])
            self.L2.delete_kth(self.cacheSize + 1)

    def _insertTL(self, task):
        # Insert a task into the threshold table, scan from left to right, eliminating tasks suppressed or expired by this task
        # Until the task finds its position, or exits the insertion process due to being suppressed by other tasks
        # Finally, update the threshold
        iFlag = False
        newTL = []
        for tTask in self.thresholdList:
            if tTask.score[self.id] == 0:
                continue
            newTL.append(tTask)
            # If it has not been inserted yet, judge
            # Since there is a guardTask, the insertion operation will end before all tasks in TL are scanned
            if not iFlag:
                # If the end time of the task scanned is earlier than the insertion task
                if tTask.eTime < task.eTime:
                    # If the task with an earlier end time has a lower score than the insertion task, the task is suppressed and deleted directly
                    if tTask.score[self.id] < task.score[self.id]:
                        newTL.pop(-1)
                # If the end time of the scanned task is later than the insertion task, the task should be inserted in front of this task (it needs to be judged once)
                else:
                    # If the task with a higher score has a later end time, the insertion task is suppressed and the insertion is canceled
                    if tTask.score[self.id] > task.score[self.id]:
                        return
                    # Otherwise, it is successfully inserted
                    newTL.pop(-1)
                    newTL.append(task)
                    newTL.append(tTask)
                    iFlag = True
        # Point to the new threshold table, and the threshold is updated to the first item in the threshold table
        self.thresholdList = newTL
        self.threshold = self.thresholdList[0].score[self.id]


    def refreshL1(self):
        # Called externally every once in a while
        # Traverse L1, delete tasks with a score of 0, and put available tasks into a new list
        newL1 = []
        for task in self.L1:
            if task.score[self.id] != 0:
                newL1.append(task)
        self.L1 = newL1

    def delL2(self, task):
        # Call the delete function of the binary search tree to delete the corresponding node
        # If the capacity is insufficient, call the initialization of L2
        # Called by the task when it expires
        self.L2.delete(task.score[self.id])
        if self.L1 > TOP_K > self.L2.root.size:
            self.initL2()

    def adaptSize(self, size):
        # Adjust the capacity of L2 and make corresponding updates:
        # If the capacity decreases, delete the redundant tasks in L2 and update the threshold table
        # If the capacity increases, no other actions are taken
        # Finally, update the value of cacheSize
        if self.L2 is None:
            return
        elif self.L2.root is None:
            return
        elif size is None:
            return
        if self.L2.root.size > size:
            for i in range(self.L2.root.size, size, -1):
                delTask = self.L2.delete_kth(i)
                # self._insertTL(delTask)
        self.cacheSize = size

    def initSB(self):
        # SB --> Skyband
        self.L1.sort(key=lambda x: x.score[self.id], reverse=True)
        self.topK = self.L1[:TOP_K]
        for task in self.topK:
            self.insertSB(task)

   def insertSB(self, task):
        self.L1.append(task)
        if task.score[self.id] < self.threshold:
            return
        task.dominance[self.id] = 0
        # Calculate the dominance number of the task
        for sbTask in self.skyband:
            if sbTask.score[self.id] >= task.score[self.id] and sbTask.eTime >= task.eTime:
                task.dominance[self.id] += 1
        if task.dominance[self.id] >= TOP_K:
            return
        self.skyband.append(task)
        task.skyband.append(self)
        # If it can be added, update the dominance number of other tasks
        delTask = []
        for sbTask in self.skyband:
            if sbTask.score[self.id] <= task.score[self.id] and sbTask.eTime <= task.eTime:
                sbTask.dominance[self.id] += 1
                # If other tasks are dominated by TOP_K times, remove them
                if sbTask.dominance[self.id] >= TOP_K:
                    delTask.append(sbTask)
                    # Eliminate the impact of the removed task
                    for _task in self.skyband:
                        if sbTask.score[self.id] >= _task.score[self.id] and sbTask.eTime >= _task.eTime:
                            _task.dominance[self.id] -= 1
        # Process the deleted tasks
        for dt in delTask:
            if self in dt.skyband:
                dt.skyband.remove(self)
            if len(self.skyband) < TOP_K:
                self.initSB()
            else:
                if dt in self.topK:
                    self.topK.remove(dt)
                    self.topK.append(self.skyband[len(self.topK)])
                    self.topK.sort(key=lambda x: x.score[self.id], reverse=True)
        # Finally, determine whether it can be added to Top_k
        if len(self.topK) == 0 or task.score[self.id] >= self.topK[-1].score[self.id]:
            self.topK.append(task)
            self.topK.sort(key=lambda x: x.score[self.id], reverse=True)
            if len(self.topK) > TOP_K:
                self.threshold = self.topK[-1].score[self.id]
                self.topK.pop(-1)

    def delSB(self, task):
        # Remove expired tasks from Skyband
        if self in task.skyband:
            task.skyband.remove(self)
        for others in self.skyband:
            if task.score[self.id] > others.score[self.id] and task.eTime > others.eTime:
                others.dominance[self.id] -= 1
        if len(self.skyband) < TOP_K:
            self.initSB()
        else:
            if task in self.topK:
                self.topK.remove(task)
                self.topK.append(self.skyband[len(self.topK)])
                self.topK.sort(key=lambda x: x.score[self.id], reverse=True)


if __name__ == '__main__':
    loadStart = time.perf_counter()
    with open('..\\..\\data\\TaskList_CD_20161101.dat', 'rb') as file:
        tasks = pickle.load(file)
    print('加载用时', time.perf_counter() - loadStart)
    testBuffer = TaskBuffer(1)
    iniTasks = tasks[:100]
    cnt = 0
    for task in iniTasks:
        task.score[1] = random.random()
        if task.score[1] < 0.9:
            continue
        print('%.3f' % task.score[1], end=' ')
        cnt += 1
        if cnt % 10 == 0:
            print('')
    testBuffer.initL1(iniTasks)
    testBuffer.initL2()
    testBuffer.L2.leftFirstSearch()
    print('--------')
    testBuffer.adaptSize(3)
    testBuffer.L2.leftFirstSearch()
    print(testBuffer.threshold)
    print(testBuffer.thresholdList)
