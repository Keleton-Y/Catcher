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
    skype(None, workerList, taskList)
    timePass = time.perf_counter() - algoStart
    print('\n', timePass, 's', timePass * 1000 / 100000, 'ms')


def batch_execute(workerFile, taskFile, taskNum, mode=None):
    # Function for batch running algorithms
    print('----------')
    print(workerFile)
    print(taskFile)
    with open(workerFile, 'rb') as worker_file:
        workerList = pickle.load(worker_file)
    print('Workers data loaded successfully')
    with open(taskFile, 'rb') as task_file:
        taskList = pickle.load(task_file)
    print('Tasks data loaded successfully')
    if mode == 'baseline':
        algoStart = time.perf_counter()
        baseline(None, workerList, taskList)
        timePass = time.perf_counter() - algoStart
        print('\n', timePass, 's', timePass * 1000 / taskNum, 'ms')
    if mode == 'history':
        algoStart = time.perf_counter()
        his_based(None, workerList, taskList)
        timePass = time.perf_counter() - algoStart
        print('\n', timePass, 's', timePass * 1000 / taskNum, 'ms')
    if mode == 'skype':
        algoStart = time.perf_counter()
        skype(None, workerList, taskList)
        timePass = time.perf_counter() - algoStart
        print('\n', timePass, 's', timePass * 1000 / taskNum, 'ms')


def skype(scContext, workerList, taskList):
    # The difference from baseline: no double-layer cache, it can be assumed that all tasks can enter L1; 
    # the threshold is not the score of the previous k-th task, but calculated.
    print('Start executing SKYPE method...')
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
    workerMap = {}
    
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
            # Remove traces of the task in each skyband
            for worker in task.skyband:
                # Remove the expired task from the Skyband
                if worker in task.skyband:
                    task.skyband.remove(worker)
                for others in worker.skyband:
                    if task.score[worker.id] > others.score[worker.id] and task.eTime > others.eTime:
                        others.dominance[worker.id] -= 1
                if len(worker.skyband) < TOP_K:
                    tWorker = workerMap[worker.id]
                    tWorker.initBuffer_2(remainList)
                    worker.initSB()
                else:
                    if task in worker.topK:
                        worker.topK.remove(task)
                        worker.topK.append(worker.skyband[len(worker.topK)])
                        worker.topK.sort(key=lambda x: x.score[worker.id], reverse=True)
        elif flag == 3:
            # Transfer the worker's list
            worker = workerList[0]
            workerList.pop(0)
            workerMap[worker.id] = worker
            leftList.append(worker)
            # Initialize cache
            worker.initBuffer_2(remainList)
        elif flag == 4:
            # Remove leaving workers
            leftList.pop(0)
        else:
            print('ERROR, flag not in 1~4')
            return



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
    batch_execute(workerFile='..\\..\\data\\WorkerList_NY_20160102_30K.dat',
                  taskFile='..\\..\\data\\TaskList_NY_20160102_100K.dat',
                  taskNum=100000, mode='skype')
    #
    '''batch_execute(workerFile='..\\..\\data\\WorkerList_CD_20161101_30K.dat',
                  taskFile='..\\..\\data\\TaskList_CD_20161101_100K.dat',
                  taskNum=100000, mode='skype')'''
    exit()
    batch_execute(workerFile='..\\..\\data\\WorkerList_NY_20160102_30K.dat',
                  taskFile='..\\..\\data\\TaskList_NY_20160102_100K.dat',
                  taskNum=100000, mode='history')
    # top_k_execute()
    # SMA_TopK()
