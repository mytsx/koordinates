import requests
import json
import time
apikey = ""

pastTime = 0


def getRequestTime(func):
    def wrap(*args, **kwargs):
        global pastTime
        startTime = time.time()
        result = func(*args, **kwargs)
        endTime = time.time()
        pastTime = endTime - startTime
        # print(pastTime)
        return result
    return wrap


@getRequestTime
def getHF(latlng):
    serviceURL = "https://maps.googleapis.com/maps/api/elevation/json?locations=" + \
        latlng.replace("\n", "")+"&key="+apikey
    # print(serviceURL)
    r = requests.get(serviceURL)
    # print(r.text)
    y = json.loads(r.text)
    elevList = []
    for result in y["results"]:
        elev = result["elevation"]
        elevList.append(elev)
    # print(elevList)
    # print(pastTime)
    return elevList, pastTime

@getRequestTime
def getHPoly(coords, samples):
    serviceURL = "https://maps.googleapis.com/maps/api/elevation/json?path=" + coords + f"&samples={samples}&key="+apikey
    r = requests.get(serviceURL)
    y = json.loads(r.text)
    elevList = []
    sorguKoordinatlari = []
    for result in y["results"]:
        elev = result["elevation"]
        location = result["location"]
        lat, lng = location["lat"], location["lng"]
        sorguKoordinatlari.append((lat,lng))
        elevList.append(elev)
    return elevList, sorguKoordinatlari, pastTime

def encodePoints(points):
    latitude = 0
    longitude = 0
    result = ""

    for point in points:
        newLatitude = round(point[0]*100000)
        newLongitude = round(point[1]*100000)
        dy = newLatitude - latitude
        dx = newLongitude - longitude
        latitude = newLatitude
        longitude = newLongitude
        dy = (dy << 1) ^ (dy >> 31)
        dx = (dx << 1) ^ (dx >> 31)
        index = ((dy + dx) * (dy + dx + 1) / 2) + dy
        while (index > 0):
            rem = int(index) & 31
            index = (index - rem) / 32
            if (index > 0):
                rem += 32
                result += "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-"[
                    rem]
    return result

# print(encodePoints([[37.96359396848452,34.7291391326945]]))
