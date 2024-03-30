# Map utility class (Chengdu)
from algorithm.utils.DistanceUtils import DistanceUtils
import xml.sax
import uuid
import pickle
import time

# Define some constants
# Physical speed  40km/h = 11.11m/s
VELOCITY = 0.0110
# Maximum index number (purpose unknown, kept for now)
MAX_INDEX_NUM = 196591
# Maximum longitude of the city
MAX_LNG = 104.4608
# Minimum longitude of the city
MIN_LNG = 103.6972
# Maximum latitude
MAX_LAT = 30.9517
# Minimum latitude
MIN_LAT = 30.3267
# Create distance utility class
distanceUtils = DistanceUtils()
# Horizontal length of the city
HORIZONTAL_LENGTH = distanceUtils.getNodeDistance(MIN_LAT, MAX_LNG, MIN_LAT, MIN_LNG)
# Vertical length of the city
VERTICAL_LENGTH = distanceUtils.getNodeDistance(MAX_LAT, MIN_LNG, MIN_LAT, MIN_LNG)
# Grid size (in meters)
GRID_SIZE = 500  # 500
# Maximum number of grid on X-axis
GRID_XNUM = int(VERTICAL_LENGTH / GRID_SIZE) + 1
# Maximum number of grid on Y-axis
GRID_YNUM = int(HORIZONTAL_LENGTH / GRID_SIZE) + 1


# Node
class NodeModel(object):
    def __init__(self):
        # id
        self.nodeId = None
        # Latitude
        self.lat = 0.0
        # Longitude
        self.lng = 0.0
        # Counter
        self.counter = 0
        # Neighbor list
        self.neighbors = []
        # X and Y coordinates of the grid it belongs to
        self.gridX = None
        self.gridY = None
        # Edge mapping: given another node's id, get the edge id
        self.edge = {}


# Edge
class EdgeModel(object):
    def __init__(self):
        # id
        self.edgeId = None
        # Starting point
        self.startNode = None
        # Endpoint
        self.endNode = None
        # List of intermediate points
        self.nodeList = []
        # Length
        self.length = 0


# Grid
class GridModel(object):
    def __init__(self, index):
        # Grid coordinates (format: '(X-axis grid number, Y-axis grid number)')
        self.index = index
        # List of points
        self.Tnode = []
        # List of edges with id
        self.edgeList = []
        # List of points with id
        self.nodeList = []
        # Set of edge ids
        self.edgeSet = set()
        # Set of node ids
        self.containNode = set()


# Map content
class ServletContext(object):
    def __init__(self):
        # Edge mapping
        self.eMap = {}
        # Node mapping
        self.nMap = {}
        # Edge list
        self.eList = []
        # Node list
        self.nList = []
        # Worker list
        self.workerList = []
        # Task list
        self.taskList = []
        # Grids
        self.grids = []
        self._initGrid()

    def _initGrid(self):
        # Add grids
        for i in range(GRID_XNUM):
            temp = []
            for j in range(GRID_YNUM):
                temp.append(GridModel("(%s,%s)" % (i, j)))
            self.grids.append(temp)

    def getScore(self, worker, task):
        # Score calculation method: original planned distance / distance after accepting the task
        extraDist = distanceUtils.getDistance(worker.sNode, task.sNode) + \
                    distanceUtils.getDistance(task.dNode, worker.dNode)
        return worker.length / (task.euclideanDis + extraDist)



# Map XML file Handler
class NewGraphHandler(xml.sax.ContentHandler):
    # Process map files and put content into nMap and eList
    def __init__(self, nMap, eList):
        """
        :param nMap: Node map
        :param eList: Edge list
        """
        self.isNode = False
        self.isEdge = False
        self.isNd = False
        self.isTag = False
        self.nMap = nMap
        self.eList = eList
        self.edge = None

    # Start element event handling
    def startElement(self, tag, attributes):
        # If the tag is "node", it's a node. Build a node object and put it into nMap (indexed by id).
        if tag == "node":
            self.isNode = True
            node = NodeModel()
            id = attributes["id"]
            node.nodeId = id
            node.lat = attributes["lat"]
            node.lng = attributes["lon"]
            self.nMap[id] = node
        # If tag is "way", it's an edge. Build an edge object.
        elif tag == "way":
            self.isEdge = True
            self.edge = EdgeModel()
            self.edge.edgeId = attributes["id"]
        # If the content is information within an edge, and the tag is "nd", it's a point on the edge.
        elif self.isEdge and tag == "nd":
            self.isNd = True
            ref = attributes["ref"]  # ref = corresponding node number
            n = self.nMap[ref]  # Get the corresponding node object via mapping
            n.counter += 1  # Increment the counter of the node on the edge
            self.edge.nodeList.append(ref)  # Add the point to the edge's nodeList (indexed by edge number)
        # If the content is information within an edge, and the tag is "tag", it indicates the type of the edge.
        elif self.isEdge and tag == "tag":
            self.isTag = True
            k = attributes["k"]
            if k == "highway":
                v = attributes["v"]
                if v in ["footway", "bridelway", "steps", "path", "cycleway", "proposed", "construction",
                         "pedestrian", "bus_stop", "crossing", "elevator"]:
                    return  # If it's a special type, ignore it.
                self.eList.append(self.edge)  # Otherwise, treat it as an edge and add it to eList

    # End element event handling
    def endElement(self, tag):
        if tag == "node":
            self.isNode = False
        elif tag == "way":
            self.isEdge = False
        elif tag == "tag":
            self.isTag = False
        elif tag == "nd":
            self.isNd = False


class GraphUtils(object):
    def __init__(self):
        pass

    def saxBigGraphImport(self, filePath, scContext):
        """
        Map data import
        :param filePath: Map path
        :param scContext: Spatial crowdsourcing overall environment
        :return: None
        """
        nMap = {}  # Node map - obtained from the map
        eMap = {}  # Edge map
        eList = []  # Edge list - obtained from the map
        nSet = set

        try:
            parser = xml.sax.make_parser()  # Create XML parser
            parser.setFeature(xml.sax.handler.feature_namespaces, 0)  # Turn off namespaces
            Handler = NewGraphHandler(nMap, eList)  # Rewrite ContextHandler
            print("-------------Start parsing-------------")
            parser.setContentHandler(Handler)  # Put the parsed XML content into nMap and eList
            parser.parse(filePath)  # Start parsing the map file
            print("end parsing with: nodes : %s  |   edges: %s" % (len(nMap), len(eList)))

            # Process the large roads in eList to obtain the adjacent relationship between each point.
            listCnt = 0
            for eModel in eList:
                if listCnt % 200 == 0:
                    print('\rEdges processed:', listCnt, end='')
                listCnt += 1
                nStart = nMap[eModel.nodeList[0]]  # Get the starting point from nMap
                nEnd = nMap[eModel.nodeList[-1]]  # Get the endpoint from nMap
                tentativeLength = 0.  # Temporary length, as only points that serve as intersections are considered, a simplified edge may contain multiple points.
                sPointer = nStart  # The starting point of the real edge
                nSet.add(nStart)  # The starting point will definitely be added to the node set.
                previousNode = sPointer
                
                # Iterate over each point on the edge
                for innerNodeId in eModel.nodeList:
                    innerNode = nMap[innerNodeId]
                    if innerNode == nStart:
                        continue  # Ignore the starting point
                    tentativeLength += distanceUtils.getDistance(previousNode, innerNode)  # Add the distance between the current point and the previous point to the tentative length
                    previousNode = innerNode  # Update previousNode for the next iteration
                    if innerNode.counter == 1 and innerNode != nEnd:
                        continue  # If it's just a point on this road and not the endpoint, no further processing is needed
                    else:
                        nEdge = EdgeModel()  # Initialize a new edge
                        nEdge.startNode = sPointer
                        nEdge.endNode = innerNode
                        nEdge.edgeId = str(uuid.uuid1()).replace("-", "").strip()
                        nEdge.length = tentativeLength
                        nEdge.nodeList.append(sPointer.nodeId)
                        nEdge.nodeList.append(innerNode.nodeId)
                        nSet.add(innerNode)  # Add the two points forming the new edge to nSet, only need to process the point at the endpoint
                        sPointer.edge[innerNode.nodeId] = nEdge.edgeId  # Update the neighbor information and the edge for the two nodes
                        sPointer.neighbors.append(innerNode.nodeId)
                        innerNode.edge[sPointer.nodeId] = nEdge.edgeId
                        innerNode.neighbors.append(sPointer.nodeId)
                        eMap[nEdge.edgeId] = nEdge  # Add the edge to eMap as the real edge in the map
                        sPointer = innerNode  # Update sPointer for the next new edge
                        tentativeLength = 0.  # Reset tentative length for the new edge

            nList = list(nSet)  # Convert set to list to get nList
            scContext.nMap = nMap  # Pass nMap and eMap to the map environment
            scContext.eMap = eMap
            print('\nBFS started')
            edList = self.BFSSearch(nMap, eMap, nList[0], scContext)  # Use BFS to find the closure, remove redundant points and edges, and then assign the obtained nList and eList to scContext (done within the function)
            print('Processing grids')
            # Process the generated edges on the map to get the grids of the map. Obtain the points and edges in the corresponding grids.
            listCnt = 0
            for e in edList:
                if listCnt % 200 == 0:
                    print('\rEdges processed:', listCnt, end='')
                listCnt += 1
                nStart = e.startNode
                nEnd = e.endNode
                xIndex = int(distanceUtils.getNodeDistance(nStart.lat, nStart.lng, MAX_LAT, nStart.lng) / GRID_SIZE)  # Calculate grid coordinates after inputting four latitude and longitude values / GRID_size
                xIndex = min(GRID_XNUM - 1, xIndex)  # Start x
                yIndex = int(distanceUtils.getNodeDistance(nStart.lat, nStart.lng, nStart.lat, MIN_LNG) / GRID_SIZE)  # Start y
                yIndex = min(GRID_YNUM - 1, yIndex)
                nStart.gridX = xIndex  # Add this point to the grid point index
                nStart.gridY = yIndex
                scContext.grids[xIndex][yIndex].containNode.add(nStart)
                xeIndex = int(distanceUtils.getNodeDistance(nEnd.lat, nEnd.lng, MAX_LAT, nEnd.lng) / GRID_SIZE)  # End x
                xeIndex = min(GRID_XNUM - 1, xeIndex)
                yeIndex = int(distanceUtils.getNodeDistance(nEnd.lat, nEnd.lng, nEnd.lat, MIN_LNG) / GRID_SIZE)  # End y
                yeIndex = min(GRID_YNUM - 1, yeIndex)
                nEnd.gridX = xeIndex  # Add the end point to the grid index as well
                nEnd.gridY = yeIndex
                scContext.grids[xeIndex][yeIndex].containNode.add(nEnd)
                if e.edgeId not in scContext.grids[xIndex][yIndex].edgeSet:  # Update the edge information in the grid index
                    scContext.grids[xIndex][yIndex].edgeList.append(e.edgeId)
                    scContext.grids[xIndex][yIndex].edgeSet.add(e.edgeId)
                if e.edgeId not in scContext.grids[xeIndex][yeIndex].edgeSet:
                    scContext.grids[xeIndex][yeIndex].edgeList.append(e.edgeId)
                    scContext.grids[xeIndex][yeIndex].edgeSet.add(e.edgeId)
            print("\nEnd of graph processing")
        except IOError:
            print("************")


    def BFSSearch(self, nMap, eMap, start, context):
        """
        Breadth-first search
        :param nMap: Nodes
        :param eMap: Edges
        :param start: Starting point
        :param context:
        :return:
        """
        stack = []  # Stack required for BFS; closeXX is essentially nodeXX
        closeList = []
        edgeList = []
        closeSet = set()
        edgeSet = set()

        stack.append(start)  # Add the starting point to the stack
        while len(stack) != 0:
            cur = stack[-1]  # Get the top of the stack
            stack.pop(-1)  # Pop the stack
            if cur.nodeId not in closeSet:  # If the point is not in closeSet, add it to the set and the list
                closeList.append(cur)
                closeSet.add(cur.nodeId)
                # For all neighbors of this point, add them to the stack and add the edges between the neighbor and this point to edgeList
                for neighborId in cur.neighbors:
                    stack.append(nMap[neighborId])
                    e = eMap[cur.edge[neighborId]]
                    if e.edgeId not in edgeSet:
                        edgeList.append(e)
                        edgeSet.add(e.edgeId)
        context.nList = closeList
        context.eList = edgeList
        print("After DFS nodeNumber: %s  |  edgeNumber:%s" % (len(closeList), len(edgeList)))
        return edgeList

    def findNode(self, lat, lng, scContext):
        """
        Find the node corresponding to the latitude and longitude on the map road network
        :param lat: Latitude
        :param lng: Longitude
        :param scContext: Map content
        :return: Node
        """
        xIndex = int(distanceUtils.getNodeDistance(lat, lng, MAX_LAT, lng) / GRID_SIZE)  # Calculate the grid location
        xIndex = min(GRID_XNUM - 1, xIndex)
        yIndex = int(distanceUtils.getNodeDistance(lat, lng, lat, MIN_LNG) / GRID_SIZE)
        yIndex = min(GRID_YNUM - 1, yIndex)
        nodeList = scContext.grids[xIndex][yIndex].containNode  # Get the nodes in the corresponding grid
        retNode = None  # Node to be returned as the answer
        distance = HORIZONTAL_LENGTH  # Find the minimum distance
        for node in nodeList:
            temp = distanceUtils.getNodeDistance(lat, lng, node.lat, node.lng)
            if temp <= 1e-3:  # If the latitude and longitude correspond to a node, return this node
                retNode = node
                break
            elif temp < distance:  # If the latitude and longitude are not a node on the map, return the nearest node
                distance = temp
                retNode = node
        return retNode


if __name__ == "__main__":
    pass
    file = open('..\\..\\data\\mapContext_CD.dat', 'rb')
    mapContext = pickle.load(file)
    print(len(mapContext.nList), len(mapContext.eList))
    exit()
    mapStart = time.perf_counter()
    mapContext = ServletContext()
    g = GraphUtils()
    g.saxBigGraphImport("..\\..\\data\\map_ChengDu", mapContext)
    print('Map parsing time:', time.perf_counter() - mapStart)
    saveStart = time.perf_counter()
    file = open('..\\..\\data\\mapContext_CD.dat', 'wb')
    pickle.dump(mapContext, file)
    file.close()
    print('Map storage time:', time.perf_counter() - saveStart)

    readStart = time.perf_counter()
    file = open('..\\..\\data\\mapContext_CD.dat', 'rb')
    mapContext = pickle.load(file)
    print(len(mapContext.nList), len(mapContext.eList))
    print('Map reading time:', time.perf_counter() - readStart, 's')
