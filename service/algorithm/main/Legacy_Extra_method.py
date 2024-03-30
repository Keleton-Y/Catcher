import time

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
    print('Successfully loaded worker data')
    with open('..\\..\\data\\TaskList_NY_20160102_100K.dat', 'rb') as task_file:
        taskList = pickle.load(task_file)
    print('Successfully loaded task data')
    # Run various algorithms to get results
    algoStart = time.perf_counter()
    timePass = time.perf_counter() - algoStart
    print('\n', timePass, 's', timePass * 1000 / 100000, 'ms')


def batch_execute(workerFile, taskFile, taskNum=1000000, mode=None):
    # Function for batch running algorithms
    print('----------')
    print(workerFile)
    print(taskFile)
    with open(workerFile, 'rb') as worker_file:
        workerList = pickle.load(worker_file)
    print('Successfully loaded worker data')
    with open(taskFile, 'rb') as task_file:
        taskList = pickle.load(task_file)
    print('Successfully loaded task data')
    #if mode == 'baseline':
    ex_baseline(None, workerList, taskList)

    print('----------')
    print(workerFile)
    print(taskFile)
    with open(workerFile, 'rb') as worker_file:
        workerList = pickle.load(worker_file)
    print('Successfully loaded worker data')
    with open(taskFile, 'rb') as task_file:
        taskList = pickle.load(task_file)
    print('Successfully loaded task data')
    #if mode == 'history':
    ex_his_based(None, workerList, taskList)

    print('----------')
    print(workerFile)
    print(taskFile)
    with open(workerFile, 'rb') as worker_file:
        workerList = pickle.load(worker_file)
    print('Successfully loaded worker data')
    with open(taskFile, 'rb') as task_file:
        taskList = pickle.load(task_file)
    print('Successfully loaded task data')
    #if mode == 'skype':
    ex_skype(None, workerList, taskList)


# Method based on historical data
def ex_his_based(scContext, workerList, taskList):
    print('Start executing historical data method...')
    algoStart = time.perf_counter()
    taskNum = len(taskList)
    enterSpend = 0
    expireSpend = 0
    # Get historical data
    with open('..\\..\\data\\TaskList_CD_20161101_100K.dat', 'rb') as task_file:
        hisList = pickle.load(task_file)
    hisData = taskHisDataModel(hisList, 0)
    # Expired task list, which stores tasks that have appeared but have not expired
    # For tasks in taskList, we focus on their sTime
    # For tasks in expireList, we focus on their eTime
    expireList = []
    for task in taskList:
        # task.eTime += random.randint(1, WAITING_TIME * 2) * 60
        expireList.append(task)
    expireList.sort(key=lambda x: x.eTime)
    remainList = []
    # Similarly, leftList contains appeared workers
    leftList = []
    # Current time, time will jump to key points
    curTime = 0
    # Current time period, if curTime doesn't belong to seg, it's considered entering a new time period, updating the cacheSize for all workers
    seg = 0
    # New task appearance ratio
    p = 0.5
    step = 0
    while len(taskList) != 0 or len(expireList) != 0:
        step += 1
        if step % 100 == 0:
            print('\rExecuted', step, 'steps  Key info:', len(taskList), len(remainList), len(workerList),
                  len(leftList), end='')
        curTime, flag = _checkTime(taskList, expireList, workerList, leftList)
        # Enter a new time period, update the cache size, and update the L1 cache for each worker
        if int(curTime / 300) != seg:
            seg = int(curTime / 300)
            try:
                p = hisData.pMap[seg]
            except KeyError:
                break
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
        stepStart = time.perf_counter()
        if flag == 1:
            # Transfer to the task list
            task = taskList[0]
            taskList.pop(0)
            remainList.append(task)
            # Traverse online workers, add task to their cache if conditions are met
            for wk in leftList:
                if wk.checkTask(task):
                    wk.insertTask(task)
            enterSpend += time.perf_counter() - stepStart
        elif flag == 2:
            # Remove expired tasks
            task = expireList[0]
            expireList.pop(0)
            remainList.remove(task)
            # Expire the task
            task.expire()
            expireSpend += time.perf_counter() - stepStart
        elif flag == 3:
            # Transfer to the worker list
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
            # Remove departing workers
            leftList.pop(0)
        else:
            print('ERROR, flag not in 1~4')
            return
    print('\n', time.perf_counter() - algoStart, 's --- enterTime', enterSpend * 1000 / taskNum, 'ms --- expireTime', expireSpend * 1000 / taskNum)



# Basic method (using k-skyband + simple threshold)
def ex_baseline(scContext, workerList, taskList):
    print('Start executing Baseline method...')
    algoStart = time.perf_counter()
    taskNum = len(taskList)
    enterSpend = 0
    expireSpend = 0
    # Expired task list, which stores tasks that have appeared but have not expired
    # For tasks in taskList, we focus on their sTime
    # For tasks in expireList, we focus on their eTime
    expireList = []
    for task in taskList:
        expireList.append(task)
    expireList.sort(key=lambda x: x.eTime)
    # Similarly, leftList contains appeared workers
    remainList = []
    leftList = []
    step = 0
    while len(taskList) != 0 or len(expireList) != 0:
        step += 1
        if step % 100 == 0:
            print('\rExecuted', step, 'steps  Key info:', len(taskList), len(remainList), len(workerList),
                  len(leftList), end='')
        curTime, flag = _checkTime(taskList, expireList, workerList, leftList)
        stepStart = time.perf_counter()
        if flag == 1:
            # Transfer to the task list
            task = taskList[0]
            taskList.pop(0)
            remainList.append(task)
            # Traverse online workers, add task to their cache if conditions are met
            for wk in leftList:
                if wk.checkTask(task):
                    task.L1.append(wk)
                    wk.buffer.insertSB(task)
            enterSpend += time.perf_counter() - stepStart
        elif flag == 2:
            # Remove expired tasks
            task = expireList[0]
            expireList.pop(0)
            remainList.remove(task)
            # Expire the task
            task.expire_2()
            expireSpend += time.perf_counter() - stepStart
        elif flag == 3:
            # Transfer to the worker list
            worker = workerList[0]
            workerList.pop(0)
            leftList.append(worker)
            # Initialize cache
            worker.initBuffer_2(remainList)
        elif flag == 4:
            # Remove departing workers
            leftList.pop(0)
        else:
            print('ERROR, flag not in 1~4')
            return
    print('\n', time.perf_counter() - algoStart, 's --- enterTime', enterSpend * 1000 / taskNum, 'ms --- expireTime', expireSpend * 1000 / taskNum)
    
    
def ex_skype(scContext, workerList, taskList):
    # Difference from baseline: no double-layer cache, all tasks can enter L1; threshold is not the score of the previous k-th task, but obtained through calculation.
    print('Start executing SKYPE method...')
    algoStart = time.perf_counter()
    taskNum = len(taskList)
    enterSpend = 0
    expireSpend = 0
    # Expired task list, which stores tasks that have appeared but have not expired
    # For tasks in taskList, we focus on their sTime
    # For tasks in expireList, we focus on their eTime
    expireList = []
    for task in taskList:
        expireList.append(task)
    expireList.sort(key=lambda x: x.eTime)
    # Similarly, leftList contains appeared workers
    remainList = []
    leftList = []
    workerMap = {}
    step = 0
    while len(taskList) != 0 or len(expireList) != 0:
        step += 1
        if step % 100 == 0:
            print('\rExecuted', step, 'steps  Key info:', len(taskList), len(remainList), len(workerList),
                  len(leftList), end='')
        curTime, flag = _checkTime(taskList, expireList, workerList, leftList)
        stepStart = time.perf_counter()
        if flag == 1:
            # Transfer to the task list
            task = taskList[0]
            taskList.pop(0)
            remainList.append(task)
            # Traverse online workers, add task to their cache if conditions are met
            for wk in leftList:
                if wk.checkTask(task):
                    task.L1.append(wk)
                    wk.buffer.insertSB(task)
            enterSpend += time.perf_counter() - stepStart
        elif flag == 2:
            # Remove expired tasks
            task = expireList[0]
            expireList.pop(0)
            remainList.remove(task)
            # Expire the task
            # Remove traces of oneself in each skyband
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
            expireSpend += time.perf_counter() - stepStart
        elif flag == 3:
            # Transfer to the worker list
            worker = workerList[0]
            workerList.pop(0)
            workerMap[worker.id] = worker
            leftList.append(worker)
            # Initialize cache
            worker.initBuffer_2(remainList)
        elif flag == 4:
            # Remove departing workers
            leftList.pop(0)
        else:
            print('ERROR, flag not in 1~4')
            return
    print('\n', time.perf_counter() - algoStart, 's --- enterTime', enterSpend * 1000 / taskNum, 'ms --- expireTime', expireSpend * 1000 / taskNum)



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
    '''batch_execute(workerFile='..\\..\\data\\WorkerList_CD_20161101_30K.dat',
                  taskFile='..\\..\\data\\TaskList_CD_20161101_100K.dat', )
    exit()
    batch_execute(workerFile='..\\..\\data\\WorkerList_NY_20160102_30K.dat',
                  taskFile='..\\..\\data\\TaskList_NY_20160102_100K.dat', )'''

    batch_execute(workerFile='..\\..\\data\\WorkerList_NY_20160102_30K.dat',
                  taskFile='..\\..\\data\\TaskList_NY_20160102_200K.dat',)
    batch_execute(workerFile='..\\..\\data\\WorkerList_NY_20160102_30K.dat',
                  taskFile='..\\..\\data\\TaskList_NY_20160102_150K.dat', )
    batch_execute(workerFile='..\\..\\data\\WorkerList_NY_20160102_30K.dat',
                  taskFile='..\\..\\data\\TaskList_NY_20160102_100K.dat', )
    batch_execute(workerFile='..\\..\\data\\WorkerList_NY_20160102_30K.dat',
                  taskFile='..\\..\\data\\TaskList_NY_20160102_50K.dat', )
    batch_execute(workerFile='..\\..\\data\\WorkerList_NY_20160102_30K.dat',
                  taskFile='..\\..\\data\\TaskList_NY_20160102_30K.dat', )

    batch_execute(workerFile='..\\..\\data\\WorkerList_NY_20160102_50K.dat',
                  taskFile='..\\..\\data\\TaskList_NY_20160102_100K.dat', )
    batch_execute(workerFile='..\\..\\data\\WorkerList_NY_20160102_40K.dat',
                  taskFile='..\\..\\data\\TaskList_NY_20160102_100K.dat', )
    batch_execute(workerFile='..\\..\\data\\WorkerList_NY_20160102_20K.dat',
                  taskFile='..\\..\\data\\TaskList_NY_20160102_100K.dat', )
    batch_execute(workerFile='..\\..\\data\\WorkerList_NY_20160102_10K.dat',
                  taskFile='..\\..\\data\\TaskList_NY_20160102_100K.dat', )

    batch_execute(workerFile='..\\..\\data\\WorkerList_NY_20160102_30K.dat',
                  taskFile='..\\..\\data\\TaskList_NY_20160102_100K_W20.dat', )
    batch_execute(workerFile='..\\..\\data\\WorkerList_NY_20160102_30K.dat',
                  taskFile='..\\..\\data\\TaskList_NY_20160102_100K_W15.dat', )
    batch_execute(workerFile='..\\..\\data\\WorkerList_NY_20160102_30K.dat',
                  taskFile='..\\..\\data\\TaskList_NY_20160102_100K_W05.dat', )
    batch_execute(workerFile='..\\..\\data\\WorkerList_NY_20160102_30K.dat',
                  taskFile='..\\..\\data\\TaskList_NY_20160102_100K_W03.dat', )

    batch_execute(workerFile='..\\..\\data\\WorkerList_CD_20161101_30K.dat',
                  taskFile='..\\..\\data\\TaskList_CD_20161101_200K.dat', )
    batch_execute(workerFile='..\\..\\data\\WorkerList_CD_20161101_30K.dat',
                  taskFile='..\\..\\data\\TaskList_CD_20161101_150K.dat', )
    batch_execute(workerFile='..\\..\\data\\WorkerList_CD_20161101_30K.dat',
                  taskFile='..\\..\\data\\TaskList_CD_20161101_100K.dat', )
    batch_execute(workerFile='..\\..\\data\\WorkerList_CD_20161101_30K.dat',
                  taskFile='..\\..\\data\\TaskList_CD_20161101_50K.dat', )
    batch_execute(workerFile='..\\..\\data\\WorkerList_CD_20161101_30K.dat',
                  taskFile='..\\..\\data\\TaskList_CD_20161101_30K.dat', )

    batch_execute(workerFile='..\\..\\data\\WorkerList_CD_20161101_50K.dat',
                  taskFile='..\\..\\data\\TaskList_CD_20161101_100K.dat', )
    batch_execute(workerFile='..\\..\\data\\WorkerList_CD_20161101_40K.dat',
                  taskFile='..\\..\\data\\TaskList_CD_20161101_100K.dat', )
    batch_execute(workerFile='..\\..\\data\\WorkerList_CD_20161101_20K.dat',
                  taskFile='..\\..\\data\\TaskList_CD_20161101_100K.dat', )
    batch_execute(workerFile='..\\..\\data\\WorkerList_CD_20161101_10K.dat',
                  taskFile='..\\..\\data\\TaskList_CD_20161101_100K.dat', )

    batch_execute(workerFile='..\\..\\data\\WorkerList_CD_20161101_30K.dat',
                  taskFile='..\\..\\data\\TaskList_CD_20161101_100K_W20.dat', )
    batch_execute(workerFile='..\\..\\data\\WorkerList_CD_20161101_30K.dat',
                  taskFile='..\\..\\data\\TaskList_CD_20161101_100K_W15.dat', )
    batch_execute(workerFile='..\\..\\data\\WorkerList_CD_20161101_30K.dat',
                  taskFile='..\\..\\data\\TaskList_CD_20161101_100K_W05.dat', )
    batch_execute(workerFile='..\\..\\data\\WorkerList_CD_20161101_30K.dat',
                  taskFile='..\\..\\data\\TaskList_CD_20161101_100K_W03.dat', )

    # top_k_execute()
    # SMA_TopK()
