# Distance calculation class
import geopy.distance
import math
EARTH_RADIUS = 6378.137


class DistanceUtils(object):
    def rad(self, d):
        """
        Calculate radians
        :param d: latitude and longitude value
        :return:
        """
        d = float(d)
        r = d * math.pi / 180.0
        return r

    def getNodeDistance(self, lat1Str, lng1Str, lat2Str, lng2Str, easy=False):
        if easy:
            # Latitude in radians
            radLat1 = self.rad(lat1Str)
            radLat2 = self.rad(lat2Str)
            # Difference in radians between starting point and endpoint
            difference = radLat1 - radLat2
            mdifference = self.rad(lng1Str) - self.rad(lng2Str)
            distance = 2 * math.asin(math.sqrt(math.pow(math.sin(difference / 2), 2)
                                               + math.cos(radLat1) * math.cos(radLat2)
                                               * math.pow(math.sin(mdifference / 2), 2)))
            distance = distance * EARTH_RADIUS
            distance = round(distance * 10000) / 100
            return distance
        p1 = [lat1Str, lng1Str]
        p2 = [lat2Str, lng2Str]
        return geopy.distance.distance(p1, p2).m

    def getDistance(self, start, end):
        """
        Calculate the distance between start and end points
        :param start: Node object
        :param end: Node object
        :return:
        """
        if start is None and end is None:
            return 0
        return self.getNodeDistance(start.lat, start.lng, end.lat, end.lng)

    def getEuDis(self, p1, p2):
        # Calculate the Euclidean distance between two points on the plane
        return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5


if __name__ == "__main__":
    dis = DistanceUtils()
    for i in range(1):
        dt = dis.getNodeDistance(-41.32, 174.81, 40.96, -5.50)
        if i % 1000 == 0:
            print(dt, i)
