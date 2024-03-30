from algorithm.model.Buffer import *
import random
from algorithm.utils.Constants import *
from algorithm.utils.GraphUtils_NewYork import *
# from algorithm.utils.GraphUtils_ChengDu import *


# SCWorker --> Worker for Spatial CrowdSourcing Task
# Workers have a duration, appearing at the start time of an order and disappearing at the end time of an order
class workerModel(object):
    def __init__(self, wid, start_time, end_time, start_node, end_node, detour_rate=MaxDetourRate):
        # Unique ID of the worker
        self.id = wid
        # Top-k results and cache of the worker
        self.buffer = TaskBuffer(wid)
        # Duration of the worker
        self.sTime = start_time
        self.eTime = start_time + 30 * 60
        # Starting point of the worker (node on the context)
        self.sNode = start_node
        # Destination of the worker (node on the context)
        self.dNode = end_node
        # Length of the worker's journey
        self.length = distanceUtils.getDistance(self.sNode, self.dNode)
        # Grids where the starting and ending points are located
        self.sGrid = None
        self.dGrid = None
        # Detour rate of the worker
        self.detour = detour_rate

    def initBuffer(self, tasks):
        # Initialize L1 with the given existing task pool through the checkTask function
        retainTasks = []
        for task in tasks:
            if self.checkTask(task):
                retainTasks.append(task)
        self.buffer.initL1(retainTasks)
        # After initializing L1, L2 can be initialized directly
        if len(self.buffer.L1) != 0:
            self.buffer.initL2()

    def initBuffer_2(self, tasks):
        # Initialization for the baseline method
        retainTasks = []
        for task in tasks:
            if self.checkTask(task):
                retainTasks.append(task)
                task.L1.append(self)
        self.buffer.initL1(retainTasks)
        # Initialize Skyband
        if len(self.buffer.L1) != 0:
            self.buffer.initSB()
        pass

    def checkTask(self, task):
        # Check if the task meets the spatiotemporal constraints of the worker
        # 1. Whether the block where the task is located is a reachable block for the worker
        leftGrid = self.sGrid
        rightGrid = self.dGrid
        leftPoint = [(leftGrid[0] + 0.5), (leftGrid[1] + 0.5)]
        rightPoint = [(rightGrid[0] + 0.5), (rightGrid[1] + 0.5)]
        trip = distanceUtils.getEuDis(leftPoint, task.sGrid) + distanceUtils.getEuDis(rightPoint, task.dGrid)
        trip *= GRID_SIZE
        trip += task.euclideanDis
        if trip > self.length * (1 + MaxDetourRate):
            return False
        task.score[self.id] = trip / self.length + random.random() * 0.0001 + random.random() * 0.00001
        # 2. Whether the worker can reach the destination before the task expires
        if task.eTime < self.sTime:
            return False
        if task.eTime < self.sTime + distanceUtils.getDistance(task.sNode, self.sNode) / VELOCITY:
            return False
        return True

    def setScore(self, task):
        # Set the score of the task with the current worker
        base = self.length
        extra = task.euclideanDis + \
                distanceUtils.getDistance(self.sNode, task.sNode) + distanceUtils.getDistance(self.dNode, task.dNode)
        task.score[self.id] = base / extra + random.random() * 0.0001 + random.random() * 0.00001

    def insertTask(self, task):
        self.buffer.addTask(task)

    def getL2Size(self):
        if self.buffer.L2.root is not None:
            return self.buffer.L2.root.size
        else:
            return 0


def generate_worker_data(filepath, context, limit):
    # The structure of workers is similar to that of tasks, and the parsing code is also similar
    workerList = []
    scanLineNum = 0
    gUtil = GraphUtils()
    workerNum = 0
    # Read data files and parse them into worker objects. Since workers should be fewer, they need to be limited by limit.
    with open(filepath) as taskFile:
        for line in taskFile:
            if scanLineNum % 50 == 0:
                print('\rProcessed', scanLineNum, 'data', end='')
            scanLineNum += 1
            if random.random() > limit / 300000:
                continue
            # Process the data on the current line
            line = line.replace('\n', '')
            # Information tuples, divide each line by comma
            infoTuples = line.split(",")
            # File format: 0id 1start timestamp 2end timestamp 3-4start latitude and longitude 5-6destination latitude and longitude
            tid = infoTuples[0]
            sTime = int(infoTuples[1])
            eTime = int(infoTuples[2])
            tStartNode = gUtil.findNode(float(infoTuples[4]), float(infoTuples[3]), context)
            tDestNode = gUtil.findNode(float(infoTuples[6]), float(infoTuples[5]), context)
            # Due to the simplification of the transportation network, some coordinates may not have nodes in the corresponding grids,
            # and the mapping node error is large. Do not use these data to generate workers. About 6% of the data is filtered out.
            if tStartNode is None or tDestNode is None:
                continue
            worker = workerModel(tid, sTime, eTime, tStartNode, tDestNode)
            workerList.append(worker)
            # Process worker grid data
            worker.sGrid = [tStartNode.gridX, tStartNode.gridY]
            worker.dGrid = [tDestNode.gridX, tDestNode.gridY]
            # Add one to the counter for easier control of the overall quantity
            workerNum += 1
            if workerNum == limit:
                break
    # Sort workers by start time
    workerList.sort(key=lambda x: x.sTime)
    return workerList


if __name__ == '__main__':
    readStart = time.perf_counter()
    file = open('..\\..\\data\\mapContext_NY.dat', 'rb')
    mapContext = pickle.load(file)
    print(len(mapContext.nList), '个点', len(mapContext.eList), '条边')
    print('读取地图用时', time.perf_counter() - readStart, 's')

    genStart = time.perf_counter()
    workers = generate_worker_data('..\\..\\data\\NY_data\\order-2016-01-02', mapContext, 20000)
    print('\n共得到', len(workers), '条有效数据')
    print('生成任务用时', time.perf_counter() - genStart, 's')

    dumpStart = time.perf_counter()
    with open('..\\..\\data\\WorkerList_NY_20160102_20K.dat', 'wb') as file:
        pickle.dump(workers, file)
    print('存储用时', time.perf_counter() - dumpStart)

    genStart = time.perf_counter()
    workers = generate_worker_data('..\\..\\data\\NY_data\\order-2016-01-02', mapContext, 30000)
    print('\n共得到', len(workers), '条有效数据')
    print('生成任务用时', time.perf_counter() - genStart, 's')

    dumpStart = time.perf_counter()
    with open('..\\..\\data\\WorkerList_NY_20160102_30K.dat', 'wb') as file:
        pickle.dump(workers, file)
    print('存储用时', time.perf_counter() - dumpStart)

    genStart = time.perf_counter()
    workers = generate_worker_data('..\\..\\data\\NY_data\\order-2016-01-02', mapContext, 40000)
    print('\n共得到', len(workers), '条有效数据')
    print('生成任务用时', time.perf_counter() - genStart, 's')

    dumpStart = time.perf_counter()
    with open('..\\..\\data\\WorkerList_NY_20160102_40K.dat', 'wb') as file:
        pickle.dump(workers, file)
    print('存储用时', time.perf_counter() - dumpStart)

    genStart = time.perf_counter()
    workers = generate_worker_data('..\\..\\data\\NY_data\\order-2016-01-02', mapContext, 50000)
    print('\n共得到', len(workers), '条有效数据')
    print('生成任务用时', time.perf_counter() - genStart, 's')

    dumpStart = time.perf_counter()
    with open('..\\..\\data\\WorkerList_NY_20160102_50K.dat', 'wb') as file:
        pickle.dump(workers, file)
    print('存储用时', time.perf_counter() - dumpStart)

    pass
