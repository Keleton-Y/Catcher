from DQN_brain import *
from algorithm.utils.Constants import TOP_K


class scEnv(object):
    def __init__(self, learn=True):
        # Using DQN, state length is 10, actions: [0 reduce cache, 1 cache unchanged, 2 increase cache]
        self.agent = Agent(10, 3)
        # Equivalent to not executing when there is no model file
        self.agent.loadModel()
        # Maintains the number of workers in each grid  gridId --> cnt
        self.workerCnt = {}
        # Saves the corresponding states of each worker  workerId --> state
        self.latestState = {}
        self.latestAction = {}
        # Total maintenance cost spent by each worker in the current time period  workerId --> cost
        self.cost = {}
        self.sumCost = 0
        # Whether the agent is to learn
        self.learn = learn

    def _getState(self, worker):
        # Returns the current environment state of the worker as an npArray
        # Obtains the current environment state of the worker
        oldState = self.latestState[worker.id].tolist()
        # Environment state format: e_{t-2}+e_{t-1}+e_{t}+[n_t]
        newState = oldState[3:9]
        n_t = [self.workerCnt[worker.sGrid[0] * 10000 + worker.sGrid[1]], len(worker.buffer.L1),
               worker.getL2Size(), worker.buffer.cacheSize]
        newState.extend(n_t)
        return np.array(newState, dtype=np.float32)

    def _initWorker(self, worker):
        self.latestState[worker.id] = np.array([0]*10, dtype=np.float32)
        self.latestAction[worker.id] = 1
        self.cost[worker.id] = 0

    def addWorker(self, worker):
        self._initWorker(worker)
        grid = worker.sGrid[0] * 10000 + worker.sGrid[1]
        cnt = 0 if grid not in self.workerCnt else self.workerCnt[grid]
        self.workerCnt[grid] = cnt + 1

    def delWorker(self, worker):
        self.workerCnt[worker.sGrid[0] * 10000 + worker.sGrid[1]] -= 1

    def updateWorker(self, worker):
        # Obtains the worker's last state, last action, reward obtained during this period, and current state
        state = self.latestState[worker.id]
        action = self.latestAction[worker.id]
        reward = -self.cost[worker.id]
        nState = self._getState(worker)
        # If it is in learn mode, store the experience and learn
        if self.learn:
            self.agent.buffer.push(state, action, reward, nState, 0)
        # Get action based on state
        nAction = self.agent.get_action(nState, self.learn)
        # Adjust the worker's cache, reset reward/cost
        worker.buffer.cacheSize = max(TOP_K, worker.buffer.cacheSize + nAction - 1)
        self.cost[worker.id] = 0
        # The old state is no longer useful, so store the current state
        self.latestState[worker.id] = nState
        self.latestAction[worker.id] = nAction


if __name__ == '__main__':
    a = [i for i in range(10)]
    a.extend(a[:6])
    print(a)
    pass
