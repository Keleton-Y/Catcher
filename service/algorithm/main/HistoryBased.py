import math
from matplotlib import pyplot as plt
import numpy as np
from algorithm.utils.Constants import *

# Get the value of Z(N_c), where p is the proportion of new tasks appearing in the current time period, and N_c is (cache capacity - k)
def _getZ(p, N_c):
    if p == 0.5:
        return (N_c + 1) * (N_c + 2)
    q = 1 - p
    term1 = 1 / q
    term2 = N_c / (q - p)
    term3_1 = (p ** 2) / (q * ((1 - 2 * p) ** 2))
    # Avoid calculation overflow, since the normal cost is within two digits, a large number can be used as INF
    if (p / q) > 1.5 and N_c > 50:
        term3_2 = 1e5
    else:
        term3_2 = (p / q) ** N_c
    return max(1, term1 + term2 + term3_1 * (term3_2 - 1))

# Get the value of the cost function, where n_s is the current size of L1
def _getCost(p, n_s, N_c):
    if N_c == 0:
        N_c = 1
    term1 = math.log2(TOP_K + N_c)
    term2 = 4 * n_s / _getZ(p, N_c)
    return term1 + term2

# Get the optimal N_c that satisfies the constraints and minimizes the cost function
# Where currentN_c is the capacity of L2 cache minus k when calling the function
# By analyzing the function, it can be seen that this function decreases first and then increases, with only one peak
def getBestSize(p, n_s, currentN_c):
    upperSize = int(currentN_c * (1 + ADAPT_RATE * 2))
    lowerSize = int(currentN_c * (1 - ADAPT_RATE))
    # If the cost is still decreasing at upperSize, the answer is upperSize
    if _getCost(p, n_s, upperSize - 1) > _getCost(p, n_s, upperSize):
        return upperSize
    # If the cost keeps increasing at lowerSize, the answer is lowerSize
    elif _getCost(p, n_s, lowerSize) < _getCost(p, n_s, lowerSize + 1):
        return lowerSize
    # Otherwise, the answer lies between the double peaks of upperSize and lowerSize
    else:
        # Because this situation is relatively rare, let's just traverse it (and usually the answer is not far from loweSize)
        # Of course, the golden section method can also be used to speed up
        scores = {lowerSize: _getCost(p, n_s, lowerSize),
                  lowerSize + 1: _getCost(p, n_s, lowerSize + 1)}
        for size in range(lowerSize + 1, upperSize):
            scores[size + 1] = _getCost(p, n_s, size+1)
            if scores[size] < scores[size-1] and scores[size] < scores[size+1]:
                return size

# Plot the graph of the cost function, showing the maintenance cost of different p and cacheSize under fixed n_s
def drawFunc():
    x = []
    z = []
    for rate in range(100, 950):
        p = rate / 1000
        x.append(p)
        tz = []
        for size in range(1, 851):
            # The function is mostly within the range below 10
            # To make the graph easier to read, limit the values in the exponential explosion area
            tz.append(min(50, _getCost(p, 500, size)))
        z.append(tz)
    X = np.asarray(x)
    Y = np.arange(1, 851)
    # Grid the X and Y
    X, Y = np.meshgrid(Y, X)
    Z = np.asarray(z)
    print(X.shape, Y.shape, Z.shape)
    # Plot the surface graph
    ax = plt.axes(projection='3d')
    ax.plot_surface(X, Y, Z, cmap=plt.get_cmap('rainbow'), edgecolor='none')
    ax.set_title('Surface plot')
    plt.show()

if __name__ == '__main__':
    pass
