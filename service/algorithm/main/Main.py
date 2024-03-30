from algorithm.utils.Constants import *
from algorithm.model.SCTask import *
from algorithm.model.SCWorker import *
from HistoryBased import *
from algorithm.model.BSTree import *
from algorithm.model.Buffer import *
import pickle


def top_k_execute():
    # Generate task list and worker list based on real dataset
    with open('..\\..\\data\\WorkerList_NY_20160102_30K.dat', 'rb') as worker_file:
        workerList = pickle.load(worker_file)
    print('Workers data loaded successfully')
    with open('..\\..\\data\\TaskList_NY_20160102_100K.dat', 'rb') as task_file:
        taskList = pickle.load(task_file)
    print('Tasks data loaded successfully')
    # Run various algorithms to obtain results
    algoStart = time.perf_counter()
    his_based(None, workerList, taskList)
    timePass = time.perf_counter() - algoStart
    print('\n', timePass, 's', timePass * 1000 / 100000, 'ms')


def batch_execute(workerFile, taskFile, taskNum, mode=None):
    # Function for batch running algorithms
    print('----------')
    print(workerFile)
    print(taskFile)
    if mode != 'history':
        with open(workerFile, 'rb') as worker_file:
            workerList = pickle.load(worker_file)
        print('Workers data loaded successfully')
        with open(taskFile, 'rb') as task_file:
            taskList = pickle.load(task_file)
        print('Tasks data loaded successfully')
        algoStart = time.perf_counter()
        baseline(None, workerList, taskList)
        timePass = time.perf_counter() - algoStart
        print('\n', timePass, 's', timePass * 1000 / taskNum, 'ms')
    if mode != 'baseline':
        with open(workerFile, 'rb') as worker_file:
            workerList = pickle.load(worker_file)
        print('Workers data loaded successfully')
        with open(taskFile, 'rb') as task_file:
            taskList = pickle.load(task_file)
        print('Tasks data loaded successfully')
        algoStart = time.perf_counter()
        his_based(None, workerList, taskList)
        timePass = time.perf_counter() - algoStart
        print('\n', timePass, 's', timePass * 1000 / taskNum, 'ms')


# Method based on historical data
def his_based(scContext, workerList, taskList):
    print('Start executing historical data method...')
    # Get historical data
    with open('..\\..\\data\\TaskList_NY_20160101_100K.dat', 'rb') as task_file:
        hisList = pickle.load(task_file)
    hisData = taskHisDataModel(hisList, 86400)
    # Invalid task list, which stores tasks that have appeared but have not expired
    # For tasks in taskList, we pay attention to their sTime
    # For tasks in expireList, we pay attention to their eTime
    expireList = []
    for task in taskList:
        expireList.append(task)
    expireList.sort(key=lambda x: x.eTime)
    remainList = []
    # Similarly, leftList stores workers that have appeared
    leftList = []
    # Current time, the time will constantly jump to key points
    curTime = 0
    # Current time period, if curTime does not belong to seg, it is considered that the time has entered a new time period,
    # for all workers to process new cacheSize
    seg = 0
    # New task appearance ratio
    p = 0.5
    step = 0
    while len(taskList) != 0 or len(expireList) != 0:
        step += 1
        if step % 100 == 0:
            print('\rExecuted', step, 'steps, Key info:', len(taskList), len(remainList), len(workerList),
                  len(leftList), end='')
        curTime, flag = _checkTime(taskList, expireList, workerList, leftList)
        # Entered a new time period, update the cache size, and update the L1 cache of each worker
        if int(curTime / 300) != seg:
            seg = int(curTime / 300)
            try:
                p = hisData.pMap[seg]
            except KeyError:
                return
            if p == 0:
                p = 0.01
            if p == 1:
                p = 0.99
            for wk in leftList:
                if len(wk.buffer.L1) < TOP_K:
                    continue
                nSize = getBestSize(p, len(wk.buffer.L1), wk.getL2Size())
                wk.buffer.adaptSize(nSize)
                if seg % 5 == 0:
                    wk.buffer.refreshL1()
        if flag == 1:
            # Transfer the task's list
            task = taskList[0]
            taskList.pop(0)
            remainList.append(task)
            # Traverse online workers, if conditions are met, add to their cache
            for wk in leftList:
                if wk.checkTask(task):
                    wk.insertTask(task)
        elif flag == 2:
            # Remove expired tasks
            task = expireList[0]
            expireList.pop(0)
            remainList.remove(task)
            # Invalidate the task
            task.expire()
        elif flag == 3:
            # Transfer the worker's list
            worker = workerList[0]
            workerList.pop(0)
            leftList.append(worker)
            # Initialize cache
            worker.initBuffer(remainList)
            # Update cache capacity
            if len(worker.buffer.L1) < TOP_K:
                continue
            worker.buffer.adaptSize(getBestSize(p, len(worker.buffer.L1), worker.getL2Size()))
        elif flag == 4:
            # Remove leaving workers
            leftList.pop(0)
        else:
            print('ERROR, flag not in 1~4')
            return
    pass


# Basic method (using k-skyband+simple threshold)
def baseline(scContext, workerList, taskList):
    print('Start executing Baseline method...')
    # Invalid task list, which stores tasks that have appeared but have not expired
    # For tasks in taskList, we pay attention to their sTime
    # For tasks in expireList, we pay attention to their eTime
    expireList = []
    for task in taskList:
        expireList.append(task)
    expireList.sort(key=lambda x: x.eTime)
    # Similarly, leftList stores workers that have appeared
    remainList = []
    leftList = []
    step = 0
    while len(taskList) != 0 or len(expireList) != 0:
        step += 1
        if step % 100 == 0:
            print('\rExecuted', step, 'steps, Key info:', len(taskList), len(remainList), len(workerList),
                  len(leftList), end='')
        curTime, flag = _checkTime(taskList, expireList, workerList, leftList)
        if flag == 1:
            # Transfer the task's list
            task = taskList[0]
            taskList.pop(0)
            remainList.append(task)
            # Traverse online workers, if conditions are met, add to their cache
            for wk in leftList:
                if wk.checkTask(task):
                    task.L1.append(wk)
                    wk.buffer.insertSB(task)
        elif flag == 2:
            # Remove expired tasks
            task = expireList[0]
            expireList.pop(0)
            remainList.remove(task)
            # Invalidate the task
            task.expire_2()
        elif flag == 3:
            # Transfer the worker's list
            worker = workerList[0]
            workerList.pop(0)
            leftList.append(worker)
            # Initialize cache
            worker.initBuffer_2(remainList)
        elif flag == 4:
            # Remove leaving workers
            leftList.pop(0)
        else:
            print('ERROR, flag not in 1~4')
            return
    pass


def _checkTime(task, expire, worker, left):
    timeMin = int(1e14)
    flag = 0
    if len(task) != 0 and task[0].sTime < timeMin:
        timeMin = task[0].sTime
        flag = 1
    if len(expire) != 0 and expire[0].eTime < timeMin:
        timeMin = expire[0].eTime
        flag = 2
    if len(worker) != 0 and worker[0].sTime < timeMin:
        timeMin = worker[0].sTime
        flag = 3
    if len(left) != 0 and left[0].eTime < timeMin:
        timeMin = left[0].eTime
        flag = 4
    return timeMin, flag


if __name__ == "__main__":

    exit()
    batch_execute(workerFile='..\\..\\data\\WorkerList_NY_20160102_30K.dat',
                  taskFile='..\\..\\data\\TaskList_NY_20160102_100K.dat',
                  taskNum=100000, mode='history')
    # top_k_execute()
    # SMA_TopK()
