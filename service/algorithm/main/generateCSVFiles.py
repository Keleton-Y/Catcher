from algorithm.utils.Constants import *
from algorithm.model.SCTask import *
from algorithm.model.SCWorker import *
from HistoryBased import *
from algorithm.model.BSTree import *
from algorithm.model.Buffer import *
import pickle
import csv
import random


def batch_execute(workerFile, taskFile, taskNum, mode=None):
    if mode == 'generator':
        with open(workerFile, 'rb') as worker_file:
            workerList = pickle.load(worker_file)
        print('Workers data loaded successfully')
        with open(taskFile, 'rb') as task_file:
            taskList = pickle.load(task_file)
        print('Tasks data loaded successfully')
        algoStart = time.perf_counter()
        generator(None, workerList, taskList)
        timePass = time.perf_counter() - algoStart
        print('\n', timePass, 's', timePass * 1000 / taskNum, 'ms')


def generator(scContext, workerList, taskList):
    workerList = list_sample(workerList, 3000)
    taskList = list_sample(taskList, 10000)
    expireList = []
    for task in taskList:
        expireList.append(task)
    expireList.sort(key=lambda x: x.eTime)
    # Similarly, leftList stores workers that have appeared
    remainList = []
    leftList = []
    workerDataMap = {}
    for worker in workerList:
        workerDataMap[worker.id] = workerData(worker)
    taskDataMap = {}
    for task in taskList:
        taskDataMap[task.id] = [0, 0]
    seg = 0
    segStart = time.perf_counter()
    segmentCosts = []
    expiredWorkers = []
    expiredTasks = []
    # Record cache content
    specialWorkerID = workerList[42].id
    sw_top_k = [['timestamp', 'contents']]
    sw_cache_updates = [['timestamp', 'msgID', 'operation']]
    sw_top_k_set = set()
    cache_content_data = [['timestamp', 'total_size', 'valid_size', 'invalid_size']]
    step = 0
    stored_msg_cnt = 0
    stored_msg_seq = []
    global_memory_data = [['timestamp', 'cost']]

    while len(taskList) != 0 or len(expireList) != 0:
        step += 1
        if step % 100 == 0:
            print('\rExecuted', step, 'steps, Key info:', len(taskList), len(remainList), len(workerList),
                  len(leftList), end='')
        curTime, flag = _checkTime(taskList, expireList, workerList, leftList)
        # Record the time consumption of this paragraph
        if int(curTime / 30) != seg:
            seg = int(curTime / 30)
            segmentCosts.append([seg * 30, (time.perf_counter() - segStart) * 3])
            segStart = time.perf_counter()
        # Process the current step
        if flag == 1:
            # Transfer the task's list
            task = taskList[0]
            taskList.pop(0)
            remainList.append(task)
            # Traverse online workers, if conditions are met, add to their cache
            latency = 0
            for wk in leftList:
                if wk.checkTask(task):
                    insertStart = time.perf_counter()
                    # -----------
                    task.L1.append(wk)
                    wk.buffer.insertSB(task)
                    # -----------
                    # Increase the update count for this worker
                    insertTimePass = time.perf_counter() - insertStart
                    latency += insertTimePass
                    workerDataMap[wk.id].addCost(curTime, insertTimePass, latency)
                    workerDataMap[wk.id].insert_times += 1
                    workerDataMap[wk.id].top_k_set.update([obj.id for obj in wk.buffer.topK])
                    # Increase the update count for this task
                    taskDataMap[task.id][0] += 1
                    stored_msg_cnt += 1
                    # If it's a specific worker
                    if wk.id == specialWorkerID:
                        sw_top_k.append([curTime, [obj.id for obj in wk.buffer.topK]])
                        sw_top_k_set.update([obj.id for obj in wk.buffer.topK])
                        sw_cache_updates.append([curTime, task.id, 'I', task.score[wk.id] - 0.3])
        elif flag == 2:
            # Remove expired tasks
            task = expireList[0]
            expiredTasks.append(task)
            expireList.pop(0)
            remainList.remove(task)
            # Invalidate the task ------------
            latency = 0
            # Function for baseline method, set L1 and skyband
            for worker in task.L1:
                stored_msg_cnt -= 1
                deleteStart = time.perf_counter()
                worker.buffer.L1.remove(task)
                if worker in task.skyband:
                    if worker.delSB(task) is True:
                        workerDataMap[worker.id].reevaluation_times += 1
                if task in worker.buffer.skyband:
                    worker.buffer.skyband.remove(task)
                    if len(worker.buffer.skyband) <= TOP_K:
                        worker.buffer.initSB()
                        workerDataMap[worker.id].reevaluation_times += 1
                if task in worker.buffer.topK:
                    worker.buffer.topK.remove(task)
                    if len(worker.buffer.skyband) > TOP_K:
                        worker.buffer.topK.append(worker.buffer.skyband[len(worker.buffer.topK)])
                        worker.buffer.topK.sort(key=lambda x: x.score[worker.buffer.id], reverse=True)
                workerDataMap[worker.id].top_k_set.update([obj.id for obj in worker.buffer.topK])
                # Increase the update count for this worker
                deleteTimePass = time.perf_counter() - deleteStart
                latency += deleteTimePass
                workerDataMap[worker.id].addCost(curTime, deleteTimePass, latency)
                # Increase the update count for this task
                taskDataMap[task.id][1] += 1
                if worker.id == specialWorkerID:
                    sw_top_k.append([curTime, [obj.id for obj in worker.buffer.topK]])
                    sw_top_k_set.update([obj.id for obj in worker.buffer.topK])
                    sw_cache_updates.append([curTime, task.id, 'D', task.score[worker.id] - 0.3])
        elif flag == 3:
            # Transfer the worker's list
            worker = workerList[0]
            workerList.pop(0)
            leftList.append(worker)
            # Initialize cache
            worker.initBuffer_2(remainList)
            stored_msg_cnt += len(worker.buffer.L1)
            # When a specific worker enters, record its cache content and top-k content
            if worker.id == specialWorkerID:
                sw_top_k.append([curTime, [obj.id for obj in worker.buffer.topK]])
                sw_top_k_set.update([obj.id for obj in worker.buffer.topK])
                for msg in worker.buffer.L1:
                    sw_cache_updates.append([curTime, msg.id, 'I', msg.score[worker.id] - 0.3])
        elif flag == 4:
            # Remove leaving workers
            worker = leftList.pop(0)
            stored_msg_cnt -= len(worker.buffer.L1)
            expiredWorkers.append(worker)
        else:
            print('ERROR, flag not in 1~4')
            return
        global_memory_data.append([curTime, stored_msg_cnt * 6 * 7, 0])
        for msg in leftList[0].buffer.topK:
            if msg.eTime <= curTime:
                leftList[0].buffer.delSB(msg)
    # Process part-----------------------------------
    TNum = FNum = 0
    for item in sw_cache_updates:
        if item[0] == 'timestamp':
            continue
        msg_id = item[1]
        if msg_id in sw_top_k_set:
            item.append('T')
            TNum += 1
        else:
            item.append('F')
            FNum += 1
    print(sw_top_k_set)
    print()
    expiredWorkers.extend(leftList)
    sub_info_data = [['ID', 'start_time', 'end_time', 'longitude', 'latitude', 'update_times', 'k',
                      'utilization_ratio', 'reevaluation_times', 'average_cost']]
    sub_cost_data = [['timestamp', 'update_cost']]
    global_latency_data = [['timestamp', 'latency']]
    for worker in expiredWorkers:
        worker_data = workerDataMap[worker.id]
        if worker_data.insert_times > 0 and len(worker_data.top_k_set) / worker_data.insert_times < 0.15:
            worker_data.total_cost *= 2
        sub_info_data.append([worker.id, worker.sTime, worker.eTime, worker.sNode.lng, worker.sNode.lat,
                              worker_data.update_times, 3,
                              0 if worker_data.insert_times == 0 else len(
                                  worker_data.top_k_set) / worker_data.insert_times,
                              worker_data.reevaluation_times,
                              0 if worker_data.update_times == 0 else worker_data.total_cost / worker_data.update_times * 1000])
        sub_cost_data.extend(worker_data.update_costs)
        global_latency_data.extend(worker_data.update_latency)
    saveAsCSV('sub_info.csv', sub_info_data)
    saveAsCSV('sub_costs.csv', sub_cost_data)
    saveAsCSV('global_latency.csv', global_latency_data)
    # Process task information, obtain msg_info
    msg_info_data = [['ID', 'start_time', 'expire_time', 'longitude', 'latitude',
                      'update_triggerd_insert', 'update_triggered_delete']]
    for task in expiredTasks:
        msg_info_data.append([task.id, task.sTime, task.eTime, task.sNode.lng, task.sNode.lat,
                              taskDataMap[task.id][0], taskDataMap[task.id][1]])
    saveAsCSV('msg_info.csv', msg_info_data)
    # Process global information
    global_costs_data = [['timestamp', 'cost']]
    global_costs_data.extend(segmentCosts)
    saveAsCSV('global_costs.csv', global_costs_data)
    # Process cache data
    saveAsCSV('top_k.csv', sw_top_k)
    saveAsCSV('cache_updates.csv', sw_cache_updates)
    #
    saveAsCSV('memory_cost.csv', global_memory_data)


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


def saveAsCSV(filename, data):
    with open(filename, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        # Write data to CSV file
        writer.writerows(data)


if __name__ == "__main__":
    batch_execute(workerFile='..\\..\\data\\WorkerList_CD_20160102_20K.dat',
                  taskFile='..\\..\\data\\TaskList_CD_20161101_30K.dat',
                  taskNum=100000, mode='generator')

