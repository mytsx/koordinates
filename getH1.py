import urllib.request
from getH import getRequestTime

# Your Bing Maps Key 
bingMapsKey = "AmIDHSRfFphz3DB2tUIL4m-p3ZlW3w28JoPO2m6AbvMT9rIe-PuNY7c393gEMRAr"

# input information
longitude = 37.96359396848452
latitude =  34.7289324365383

pastTime = 0

destination = "1427 Alderbrook Ln San Jose CA 95129"

encodedDest = urllib.parse.quote(destination, safe='')

# routeUrl = "http://dev.virtualearth.net/REST/V1/Routes/Driving?wp.0=" + str(latitude) + "," + str(longitude) + "&wp.1=" + encodedDest + "&key=" + bingMapsKey
def getHF_method(longitude, latitude):
    routeUrl = f"https://dev.virtualearth.net/REST/v1/Elevation/List?points={longitude},{latitude}&key={bingMapsKey}"
    print(routeUrl)
    request = urllib.request.Request(routeUrl)
    response = urllib.request.urlopen(request)
    result = int(str(response.read()).split("elevations")[1].split("zoom")[0].replace("\":[","").replace("],\"", ""))
    return result

@getRequestTime
def getHF_method1(latlng): #50 şer izin veriyor sanırsam
    routeUrl = f"https://dev.virtualearth.net/REST/v1/Elevation/List?points={latlng}&key={bingMapsKey}"
    print(routeUrl)
    request = urllib.request.Request(routeUrl)
    response = urllib.request.urlopen(request)
    print("geçenSüre: ", pastTime)
    # result = int(str(response.read()).split("elevations")[1].split("zoom")[0].replace("\":[","").replace("],\"", ""))

    return response, pastTime

getHF_method(longitude, latitude)