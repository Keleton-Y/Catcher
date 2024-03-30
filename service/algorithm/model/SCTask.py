import random

from algorithm.utils.Constants import *
from algorithm.utils.GraphUtils_NewYork import *
# from algorithm.utils.GraphUtils_ChengDu import *
# SCTask --> Spatial CrowdSourcing Task


class taskModel(object):
    def __init__(self, tid, start_time, start_node, end_node):
        # Unique ID of the task
        self.id = tid
        # Start time of the task
        self.sTime = start_time
        # Expiration time of the task, i.e., start time + tolerable waiting time
        self.eTime = start_time + random.randint(1, WAITING_TIME * 2) * 60
        # Starting point of the task (node on the context)
        self.sNode = start_node
        # Destination of the task (node on the context)
        self.dNode = end_node
        # Grids where the starting and ending points are located
        self.sGrid = None
        self.dGrid = None
        # Where the task is stored in TopK results and L2 cache, stored as a set, content stored as worker objects (pointers)
        self.topK = set()
        self.L2 = set()
        # Shortest Euclidean distance and shortest distance on the road network between the starting and ending points, preprocessed to avoid repeated calculations
        self.euclideanDis = distanceUtils.getDistance(start_node, end_node)
        self.trueDis = None
        # Scores of the task in various worker caches, mapped using a MAP, which is more convenient in the task. Mapping method: worker ID --> score
        self.score = {}
        # In the baseline method, the dominance count of the task in the skyband of various worker caches
        self.dominance = {}
        # Where the task is in the skyband and L1 of which caches in the baseline method
        self.skyband = []
        self.L1 = []

    def expire(self):
        # After the task expires, set the scores of the task in all workers to zero, and then directly update the L1 of each worker
        for key in self.score:
            self.score[key] = 0
        # Traverse the task's L2 set, and then call the delete function of the corresponding worker's L2 to update it
        for worker in self.L2:
            worker.buffer.delL2(self)

    def expire_2(self):
        # Function for the baseline method, set L1 and skyband
        for worker in self.L1:
            worker.buffer.L1.remove(self)
        # Delete the traces of oneself in various skybands
        for worker in self.skyband:
            worker.delSB(self)


class workerData(object):
    def __init__(self, _worker):
        self.worker = _worker
        self.update_times = 0
        self.update_costs = []
        self.update_latency = []
        self.tag = False
        # ---
        self.top_k_set = set()
        self.contained_set = []
        self.insert_times = 0
        self.reevaluation_times = 0
        self.total_cost = 0

    def addCost(self, timeStamp, cost, latency):
        self.update_costs.append([timeStamp, cost])
        self.update_latency.append([timeStamp, latency])
        self.update_times += 1
        self.total_cost += cost


class taskHisDataModel(object):
    def __init__(self, tasks, offset=0):
        # pMap stores the proportion of 'new tasks appearing in the corresponding period' in all updates in history
        self.pMap = {}
        self.tasks = tasks
        self._initQMap(offset)
        pass

    def _initQMap(self, offset):
        sumMap = {}
        qCntMap = {}
        segSet = set()
        for task in self.tasks:
            sSeg = int((task.sTime + offset) / 300)
            eSeg = int((task.eTime + offset) / 300)
            segSet.add(sSeg)
            segSet.add(eSeg)
        for seg in segSet:
            sumMap[seg] = 0
            qCntMap[seg] = 0
        for task in self.tasks:
            sSeg = int((task.sTime + offset) / 300)
            eSeg = int((task.eTime + offset) / 300)
            sumMap[sSeg] += 1
            sumMap[eSeg] += 1
            qCntMap[sSeg] += 1
        for seg in sumMap:
            self.pMap[seg] = qCntMap[seg] / sumMap[seg]


def generate_task_data(filepath, context, limit, sumNum):
    # Parsed task list
    taskList = []
    scanLineNum = 0
    gUtil = GraphUtils()
    threshold = limit / sumNum
    # Read data files and parse them into task objects
    with open(filepath) as taskFile:
        for line in taskFile:
            if scanLineNum % 50 == 0:
                print('\rProcessed', scanLineNum, 'data', end='')
            scanLineNum += 1
            if random.random() > threshold:
                continue
            line = line.replace('\n', '')
            infoTuples = line.split(",")  # Information tuples, divide each line by space
            # File format: 0id 1start timestamp 2end timestamp 3-4start latitude and longitude 5-6destination latitude and longitude
            tid = infoTuples[0]
            tStart = int(infoTuples[1])
            tStartNode = gUtil.findNode(float(infoTuples[4]), float(infoTuples[3]), context)
            tDestNode = gUtil.findNode(float(infoTuples[6]), float(infoTuples[5]), context)
            # Due to the simplification of the transportation network, some coordinates may not have nodes in the corresponding grids,
            # and the mapping node error is large. Do not use these data to generate tasks. About 6% of the data is filtered out.
            if tStartNode is None or tDestNode is None:
                continue
            task = taskModel(tid, tStart, tStartNode, tDestNode)
            taskList.append(task)
            # Process task grid data
            task.sGrid = [tStartNode.gridX, tStartNode.gridY]
            task.dGrid = [tDestNode.gridX, tDestNode.gridY]
    taskList.sort(key=lambda x: x.sTime)  # Ascending order
    return taskList


def printTask(task):
    # Output some information about the task
    tsNode = task.sNode
    tdNode = task.dNode
    # print('----------')
    print(task.id, task.sTime, task.eTime, task.euclideanDis, task.sGrid, task.dGrid)
    print(tsNode.lat, tsNode.lng, tsNode.counter, tsNode.gridX, tsNode.gridY)
    print(tdNode.lat, tdNode.lng, tdNode.counter, tdNode.gridX, tdNode.gridY)


if __name__ == '__main__':

    readStart = time.perf_counter()
    file = open('..\\..\\data\\mapContext_NY.dat', 'rb')
    mapContext = pickle.load(file)
    print(len(mapContext.nList), '个点', len(mapContext.eList), '条边')
    print('读取地图用时', time.perf_counter() - readStart, 's')

    genStart = time.perf_counter()
    tasks = generate_task_data('..\\..\\data\\NY_data\\order-2016-01-01', mapContext, 100000, 340000)
    print('\n共得到', len(tasks), '条有效数据')
    print('生成任务用时', time.perf_counter() - genStart, 's')
    dumpStart = time.perf_counter()
    with open('..\\..\\data\\TaskList_NY_20160101_100K.dat', 'wb') as file:
        pickle.dump(tasks, file)
    print('存储用时', time.perf_counter() - dumpStart)
    '''
    genStart = time.perf_counter()
    tasks = generate_task_data('..\\..\\data\\NY_data\\order-2016-01-02', mapContext, 150000, 300000)
    print('\n共得到', len(tasks), '条有效数据')
    print('生成任务用时', time.perf_counter() - genStart, 's')
    dumpStart = time.perf_counter()
    with open('..\\..\\data\\TaskList_NY_20160102_150K.dat', 'wb') as file:
        pickle.dump(tasks, file)
    print('存储用时', time.perf_counter() - dumpStart)

    genStart = time.perf_counter()
    tasks = generate_task_data('..\\..\\data\\NY_data\\order-2016-01-02', mapContext, 50000, 300000)
    print('\n共得到', len(tasks), '条有效数据')
    print('生成任务用时', time.perf_counter() - genStart, 's')
    dumpStart = time.perf_counter()
    with open('..\\..\\data\\TaskList_NY_20160102_50K.dat', 'wb') as file:
        pickle.dump(tasks, file)
    print('存储用时', time.perf_counter() - dumpStart)

    genStart = time.perf_counter()
    tasks = generate_task_data('..\\..\\data\\NY_data\\order-2016-01-02', mapContext, 30000, 300000)
    print('\n共得到', len(tasks), '条有效数据')
    print('生成任务用时', time.perf_counter() - genStart, 's')
    dumpStart = time.perf_counter()
    with open('..\\..\\data\\TaskList_NY_20160102_30K.dat', 'wb') as file:
        pickle.dump(tasks, file)
    print('存储用时', time.perf_counter() - dumpStart)
'''
    pass
