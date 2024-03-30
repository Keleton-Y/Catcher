from matplotlib.collections import LineCollection

from algorithm.model.SCTask import *
from algorithm.model.SCWorker import *
from env import *
import pickle
import numpy as np
import matplotlib.pyplot as plt


def run(workerFile, taskFile, learn=False, episode=0):
    print('Start running the DQN method...')
    algoStart = time.perf_counter()
    # Generate task list and worker list based on real dataset
    with open(workerFile, 'rb') as worker_file:
        workerList = pickle.load(worker_file)
    print('Successfully loaded worker data')
    with open(taskFile, 'rb') as task_file:
        taskList = pickle.load(task_file)
    print('Successfully loaded task data')
    env = scEnv(learn=learn)
    print('Successfully loaded SC environment and DQN model')
    taskNum  = len(taskList)
    enterSpend = 0
    expireSpend = 0
    # -----
    expireList = []
    for task in taskList:
        expireList.append(task)
    expireList.sort(key=lambda x: x.eTime)
    # Similarly, leftList contains appeared workers
    remainList = []
    leftList = []
    # Current time period, if curTime doesn't belong to seg, it's considered entering a new time period, updating the cacheSize for all workers
    seg = 0
    timeSum = 0
    # Find the earliest time from the four lists and make it the current time
    # |  1 If the earliest is in the task list, execute the action to insert a new task
    # |  2 If the earliest is in the expired list, execute the task invalidation
    # |  3 If the earliest is in the worker list, execute the initialization of a new worker
    # |  4 If the earliest is in the left list, just remove the worker from the list
    # This implementation is based on the static view of the environment
    # --- Execute until all tasks expire ---
    runCost = []
    runCostStart = time.perf_counter()
    step = 0
    print('Start running')
    while len(taskList) != 0 or len(expireList) != 0:
        step += 1
        if step % 100 == 0:
            print('\rExecuted', step, 'steps  Key info:', len(taskList), len(remainList), len(workerList),
                  len(leftList), end='')
        curTime, flag = _checkTime(taskList, expireList, workerList, leftList)
        # In the DRL method, adjust the worker's cache capacity every minute
        if int(curTime / 60) != seg:
            seg = int(curTime / 60)
            # Call env here to update the cacheSize of workers and train DQN
            for worker in leftList:
                env.updateWorker(worker)
            if learn:
                if len(env.agent.buffer.buffer) > BATCH_SIZE:
                    env.agent.replay(len(leftList))
                if seg % 5 == 0:
                    env.agent.target_update()
            if len(runCost) < 1440:
                runCost.append(time.perf_counter() - runCostStart)
            runCostStart = time.perf_counter()
        stepStart = time.perf_counter()
        if flag == 1:
            # Transfer to the task list
            task = taskList[0]
            taskList.pop(0)
            remainList.append(task)
            # Traverse online workers, add task to their cache if conditions are met
            # sumStart = time.perf_counter()
            for wk in leftList:
                if wk.checkTask(task):
                    wk.insertTask(task)
            enterSpend += time.perf_counter() - stepStart
        elif flag == 2:
            # Remove expired tasks
            # sumStart = time.perf_counter()
            task = expireList[0]
            expireList.pop(0)
            remainList.remove(task)
            # Expire the task
            task.expire()
            expireSpend += time.perf_counter() - stepStart
        elif flag == 3:
            # Transfer to the worker list
            worker = workerList[0]
            leftList.append(worker)
            env.addWorker(worker)
            workerList.pop(0)
            # Initialize cache
            worker.initBuffer(remainList)
        elif flag == 4:
            # Remove departing workers
            worker = leftList[0]
            leftList.pop(0)
            env.delWorker(worker)
        else:
            print('ERROR, flag not in 1~4')
            return
    if learn:
        env.agent.saveModel()
        env.agent.saveModel(str(episode))
        print(env.sumCost)
    print(workerFile, taskFile)
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


if __name__ == '__main__':
    '''run(workerFile='..\\..\\data\\WorkerList_NY_20160102_30K.dat',
        taskFile='..\\..\\data\\TaskList_NY_20160102_100K.dat')
    run(workerFile='..\\..\\data\\WorkerList_CD_20161101_30K.dat',
        taskFile='..\\..\\data\\TaskList_CD_20161101_100K.dat')'''
    run(workerFile='..\\..\\data\\WorkerList_NY_20160102_30K.dat',
        taskFile='..\\..\\data\\TaskList_NY_20160102_200K.dat')
    run(workerFile='..\\..\\data\\WorkerList_NY_20160102_30K.dat',
        taskFile='..\\..\\data\\TaskList_NY_20160102_150K.dat')
    run(workerFile='..\\..\\data\\WorkerList_NY_20160102_30K.dat',
        taskFile='..\\..\\data\\TaskList_NY_20160102_100K.dat')
    run(workerFile='..\\..\\data\\WorkerList_NY_20160102_30K.dat',
        taskFile='..\\..\\data\\TaskList_NY_20160102_50K.dat')
    run(workerFile='..\\..\\data\\WorkerList_NY_20160102_30K.dat',
        taskFile='..\\..\\data\\TaskList_NY_20160102_30K.dat')

    run(workerFile='..\\..\\data\\WorkerList_NY_20160102_50K.dat',
        taskFile='..\\..\\data\\TaskList_NY_20160102_100K.dat')
    run(workerFile='..\\..\\data\\WorkerList_NY_20160102_40K.dat',
        taskFile='..\\..\\data\\TaskList_NY_20160102_100K.dat')
    run(workerFile='..\\..\\data\\WorkerList_NY_20160102_20K.dat',
        taskFile='..\\..\\data\\TaskList_NY_20160102_100K.dat')
    run(workerFile='..\\..\\data\\WorkerList_NY_20160102_10K.dat',
        taskFile='..\\..\\data\\TaskList_NY_20160102_100K.dat')

    run(workerFile='..\\..\\data\\WorkerList_NY_20160102_30K.dat',
        taskFile='..\\..\\data\\TaskList_NY_20160102_100K_W20.dat')
    run(workerFile='..\\..\\data\\WorkerList_NY_20160102_30K.dat',
        taskFile='..\\..\\data\\TaskList_NY_20160102_100K_W15.dat')
    run(workerFile='..\\..\\data\\WorkerList_NY_20160102_30K.dat',
        taskFile='..\\..\\data\\TaskList_NY_20160102_100K_W05.dat')
    run(workerFile='..\\..\\data\\WorkerList_NY_20160102_30K.dat',
        taskFile='..\\..\\data\\TaskList_NY_20160102_100K_W03.dat')

    run(workerFile='..\\..\\data\\WorkerList_CD_20161101_30K.dat',
        taskFile='..\\..\\data\\TaskList_CD_20161101_200K.dat')
    run(workerFile='..\\..\\data\\WorkerList_CD_20161101_30K.dat',
        taskFile='..\\..\\data\\TaskList_CD_20161101_150K.dat')
    run(workerFile='..\\..\\data\\WorkerList_CD_20161101_30K.dat',
        taskFile='..\\..\\data\\TaskList_CD_20161101_100K.dat')
    run(workerFile='..\\..\\data\\WorkerList_CD_20161101_30K.dat',
        taskFile='..\\..\\data\\TaskList_CD_20161101_50K.dat')
    run(workerFile='..\\..\\data\\WorkerList_CD_20161101_30K.dat',
        taskFile='..\\..\\data\\TaskList_CD_20161101_30K.dat')

    run(workerFile='..\\..\\data\\WorkerList_CD_20161101_50K.dat',
        taskFile='..\\..\\data\\TaskList_CD_20161101_100K.dat')
    run(workerFile='..\\..\\data\\WorkerList_CD_20161101_40K.dat',
        taskFile='..\\..\\data\\TaskList_CD_20161101_100K.dat')
    run(workerFile='..\\..\\data\\WorkerList_CD_20161101_20K.dat',
        taskFile='..\\..\\data\\TaskList_CD_20161101_100K.dat')
    run(workerFile='..\\..\\data\\WorkerList_CD_20161101_10K.dat',
        taskFile='..\\..\\data\\TaskList_CD_20161101_100K.dat')

    run(workerFile='..\\..\\data\\WorkerList_CD_20161101_30K.dat',
        taskFile='..\\..\\data\\TaskList_CD_20161101_100K_W20.dat')
    run(workerFile='..\\..\\data\\WorkerList_CD_20161101_30K.dat',
        taskFile='..\\..\\data\\TaskList_CD_20161101_100K_W15.dat')
    run(workerFile='..\\..\\data\\WorkerList_CD_20161101_30K.dat',
        taskFile='..\\..\\data\\TaskList_CD_20161101_100K_W05.dat')
    run(workerFile='..\\..\\data\\WorkerList_CD_20161101_30K.dat',
        taskFile='..\\..\\data\\TaskList_CD_20161101_100K_W03.dat')
    pass
