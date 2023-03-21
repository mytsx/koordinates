from getH import getHF, encodePoints
# from getH1 import getHF_method1
from fastkml import kml, geometry
import pyproj, math, sys
geod = pyproj.Geod(ellps='WGS84')

def getCoordinates(kmlFile):
    coordinates = []
    with open(kmlFile) as kml_file:
        doc = kml_file.read().encode('utf-8')
        k = kml.KML()
        k.from_string(doc)
        for feature0 in k.features():
            print("{}, {}".format(feature0.name, feature0.description))
            for feature1 in feature0.features():
                if isinstance(feature1.geometry, geometry.Polygon):
                    polygon = feature1.geometry
                    for coord in polygon.exterior.coords:
                        # these are long, lat tuples
                        coordinates.append(coord)
    if coordinates:
        return coordinates
    else:
        return False


def getDistance(x, y):
    print(x, y)
    lat0, lon0 = x
    lat1, lon1 = y

    azimuth1, azimuth2, distance = geod.inv(lon0, lat0, lon1, lat1)
    return distance
atlama = 100


koordinatlar = getCoordinates("ff.kml")
lats = []
lons = []
coords = []
for koordinat in koordinatlar:
    lat = koordinat[0]
    lats.append(lat)
    lon = koordinat[1]
    lons.append(lon)
    latlon = lat, lon
    # latlon = pgh.encode(lat, lon, precision=5)

    coords.append(latlon)




maxX, minX = max(lats), min(lats)
maxY, minY = max(lons), min(lons)
print(maxX, minX)
print(maxY, minY)
minN =  minY, minX
maxN =  maxY, maxX

distance = getDistance(minN,maxN)
print("mesafe = ", distance)


xRange = maxN[0] - minN[0]
yRange = maxN[1] - minN[1]

leftBottom = minN
leftTop = maxN[0], minN[1]
rightBottom = minN[0], maxN[1]
rightTop = maxN[0], maxN[1]
print("leftBottom: ", leftBottom)
print("rightTop: ", rightTop)
yDistance_ = getDistance(leftBottom, leftTop)
xDistance_ = getDistance(leftBottom, rightBottom)
print("yDistance_ = ", yDistance_)
print("yRange = ", yRange )
print("xDistance_ = ", xDistance_)
print("xRange = ", xRange )

x0, y0 = minN
x1, y1 = maxN

xLer = []
yLer = []
for i in range(0, int(xDistance_), atlama):
    xN = x0 + ((xRange*i)/xDistance_)
    xLer.append(xN)
xLer.append(x1)
for i in range(0, int(yDistance_), atlama):
    yN = y0 + ((yRange*i)/yDistance_)
    yLer.append(yN)
yLer.append(y1)
syc = 0

from shapely import geometry
from shapely.geometry import Point, Polygon
poly = geometry.Polygon([[p[0], p[1]] for p in coords])
print(poly.wkt)
alaninIcindekiNoktalar = []
pxLer = []
noktalar = []
for yn in xLer:
    for xn in yLer:
        syc +=1
        px = Point(xn, yn)
        nokta = xn, yn
        if px.within(poly):

            noktalar.append(str(nokta[1])+","+str(nokta[0]))
            # noktalar.append(encodePoints([[nokta[1], nokta[0]]]))
            # print(str(nokta[1])+","+str(nokta[0]))
            # print(encodePoints([[nokta[1], nokta[0]]]))

            alaninIcindekiNoktalar.append(nokta)
            pxLer.append(px)
print("döngü", syc, "kere çalıştı")
print( f"Alanın içinde {atlama} metre aralıklarla {len(alaninIcindekiNoktalar)} nokta bulunmaktadır.")
if not int(input("devam etmek istermisiniz?[1 devam 0 iptal]:")):
    sys.exit()

polyN = geometry.Polygon(px for px in pxLer)

k = kml.KML()
ns = '{http://www.opengis.net/kml/2.2}'
d = kml.Document(ns, 'docid', 'doc name', 'doc description')
k.append(d)
f = kml.Folder(ns, 'fid', 'f name', 'f description')
d.append(f)
nf = kml.Folder(ns, 'nested-fid', 'nested f name', 'nested f description')
f.append(nf)
f2 = kml.Folder(ns, 'id2', 'name2', 'description2')
d.append(f2)
p = kml.Placemark(ns, 'id', 'name', 'description')
p.geometry =  polyN
# for px in pxLer:
#     p.geometry = px
f2.append(p)
testKml = open("test.kml", "w+")
print (k.to_string(prettyprint=True), file=testKml, flush=True)





print(xLer[0], xLer[-1])
print(yLer[0], yLer[-1])

print(minN[0], maxN[0])
print(minN[1], maxN[1])



sorguList, sorgu, syc  = [], "", 0
if len(noktalar) > 400:
    kacarKacar = 400
else:
    kacarKacar = len(noktalar)
for nokta in noktalar:
    sorgu+=nokta+"|"
    syc+=1
    if syc == kacarKacar or ((len(sorguList)) != 0 and (len(noktalar) - len(sorguList)*kacarKacar) == syc):
        sorguList.append(sorgu)
        sorgu, syc = "", 0

pastTimes = []
elevLer = []
print(sorgu[:-1])
for sorgu in sorguList:
    elevList, pastTime = getHF(sorgu[:-1]) #elevList, pastTime
    elevLer.extend(elevList)
    pastTimes.append(pastTime)

print(len(sorguList))
print(len(noktalar))
from statistics import mean

print("sorgulanan nokta adeti: ", len(elevLer))
print("max(elevLer) = ", max(elevLer))
print("min(elevLer) = ", min(elevLer))
print("avarage(pastTimes): ", mean(pastTimes))
print("toplam geçen süre: ", sum(pastTimes))



import simplekml
kml = simplekml.Kml()


# noktalar.append(str(nokta[1])+","+str(nokta[0]))
coords_ = [(nokta.split(",")[::-1]) for nokta in noktalar]
for coord in coords_:
    kml.newpoint(name="yükseklik nokaları", coords=[coord])
kml.save("botanicalgarden.kml")