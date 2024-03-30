from matplotlib.collections import LineCollection

from algorithm.model.SCTask import *
from algorithm.model.SCWorker import *
from env import *
import pickle
import numpy as np
import matplotlib.pyplot as plt


def run(workerFile, taskFile, learn=False, episode=0, taskSum=100000):
    print('Starting DQN method...')
    # Generate task list and worker list based on real dataset
    with open(workerFile, 'rb') as worker_file:
        workerList = pickle.load(worker_file)
    print('Worker data loaded successfully')
    with open(taskFile, 'rb') as task_file:
        taskList = pickle.load(task_file)
    print('Task data loaded successfully')
    env = scEnv(learn=learn)
    print('SC environment and DQN model loaded successfully')
    # -----
    expireList = []
    for task in taskList:
        expireList.append(task)
    expireList.sort(key=lambda x: x.eTime)
    # Similarly, leftList contains workers that have appeared
    remainList = []
    leftList = []
    # Current time period, if curTime does not belong to seg, it is considered to have entered a new time period,
    # and cacheSize of all workers is processed
    seg = 0
    timeSum = 0
    # Find the earliest time from the four lists and make it the current time
    # |  1 If the earliest is in the task list, perform the action of inserting a new task
    # |  2 If the earliest is in the expiration list, invalidate the task
    # |  3 If the earliest is in the worker list, initialize a new worker
    # |  4 If the earliest is in the left list, only remove the worker from the list
    # The basis of this implementation method is to consider the environment as static
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
        # In the DRL method, adjust the cache capacity of workers once per minute
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
        timeStart = time.perf_counter()
        if flag == 1:
            # Transfer tasks to the list
            task = taskList[0]
            taskList.pop(0)
            remainList.append(task)
            # Traverse online workers, if conditions are met, add to their cache
            # sumStart = time.perf_counter()
            for wk in leftList:
                if wk.checkTask(task):
                    insertStart = time.perf_counter()
                    wk.insertTask(task)
                    env.cost[wk.id] += time.perf_counter() - insertStart
            # env.sumCost += time.perf_counter() - sumStart
        elif flag == 2:
            # Remove expired tasks
            # sumStart = time.perf_counter()
            task = expireList[0]
            expireList.pop(0)
            remainList.remove(task)
            # Make the task expire
            task.expire()
            # env.sumCost += time.perf_counter() - sumStart
        elif flag == 3:
            # Transfer workers to the list
            worker = workerList[0]
            leftList.append(worker)
            env.addWorker(worker)
            workerList.pop(0)
            # Initialize cache
            worker.initBuffer(remainList)
        elif flag == 4:
            # Remove leaving workers
            worker = leftList[0]
            leftList.pop(0)
            env.delWorker(worker)
        else:
            print('ERROR, flag not in 1~4')
            return
        timeSum += time.perf_counter() - timeStart
    if learn:
        env.agent.saveModel()
        env.agent.saveModel(str(episode))
        print(env.sumCost)
    print(workerFile, taskFile)
    print(timeSum * 1000 / taskSum, 'ms')


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
    with open('..\\..\\data\\CD_data\\runCost_CD.dat', 'rb') as file:
        runCost = pickle.load(file)
    line = [0.11] * len(runCost)
    line = np.array(line)
    runCost = np.array(runCost)
    plt.plot(runCost)
    plt.plot(line, linestyle='--', color='grey', linewidth='2')
    plt.show()
    exit()
    run(workerFile='..\\..\\data\\WorkerList_NY_20160102_10K.dat',
        taskFile='..\\..\\data\\TaskList_NY_20160102_30K.dat',
        taskSum=30000)
    pass
