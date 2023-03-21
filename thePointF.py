from PyQt5 import QtWidgets, uic
import sys, simplekml, os
from PyQt5.QtWidgets import   QFileDialog, QMessageBox
import pyproj, sys
geod = pyproj.Geod(ellps='WGS84')
from fastkml import kml, geometry
from shapely import geometry
from shapely.geometry import Point, LineString
from statistics import mean
from getH import getHF, getHPoly
import numpy as np

class Ui(QtWidgets.QWidget):
    def __init__(self):
        super(Ui, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('alan_analiz.ui', self) # Load the .ui file
        self.kmlFilePath = ""
        self.kmlSavePath = ""
        self.atlama = self.pointsRangeSpinBox.value()
        print("self.atlama = ", self.atlama)
        self.initUI()

    def lineerRegrasyon(self):
        # model = LinearRegression()
        pass

    def getDistance(self, x, y):
        # print(x, y)
        lat0, lon0 = x
        lat1, lon1 = y

        azimuth1, azimuth2, distance = geod.inv(lon0, lat0, lon1, lat1)
        return distance
    def getCoordinates(self, kmlFile):
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
    def openFileNameDialog(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","Kml Files (*.kml)", options=options)
        if fileName:
            self.kmlFilePath = fileName
            self.firstAnalysis()
            
    def saveFileDialog(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()","","Kml Files (*.kml)", options=options)
        if fileName:
            self.kmlSavePath = fileName
            self.savePoints()
            self.savedKmlLinkLBL.setText(f"<a href={fileName}>{fileName}</a>")

    def show_warning_messagebox(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
    
        # setting message for Message Box
        msg.setText("kml dosyası hatalı!!!")
        
        # setting Message box window title
        msg.setWindowTitle("HATA")
        
        # declaring buttons on Message Box
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        
        # start the app
        retval = msg.exec_()

    def firstAnalysis(self):
        try:
            koordinatlar = self.getCoordinates(self.kmlFilePath)
            lats = []
            lons = []
            self.coords = []
            for koordinat in koordinatlar:
                lat = koordinat[0]
                lats.append(lat)
                lon = koordinat[1]
                lons.append(lon)
                latlon = lat, lon

                self.coords.append(latlon)
        except:
            self.show_warning_messagebox()
            return
        self.poly = geometry.Polygon([[p[0], p[1]] for p in self.coords])
        print(self.poly.wkt)
        

        maxX, minX = max(lats), min(lats)
        maxY, minY = max(lons), min(lons)
        print(maxX, minX)
        print(maxY, minY)
        minN =  minY, minX
        maxN =  maxY, maxX

        distance = self.getDistance(minN,maxN)
        print("mesafe = ", distance)

        self.xRange = maxN[0] - minN[0]
        self.yRange = maxN[1] - minN[1]

        leftBottom = minN
        leftTop = maxN[0], minN[1]
        rightBottom = minN[0], maxN[1]
        rightTop = maxN[0], maxN[1]
        print("leftBottom: ", leftBottom)
        print("rightTop: ", rightTop)
        self.yDistance_ = self.getDistance(leftBottom, leftTop)
        self.xDistance_ = self.getDistance(leftBottom, rightBottom)
        print("yDistance_ = ", self.yDistance_)
        print("yRange = ", self.yRange )
        print("xDistance_ = ", self.xDistance_)
        print("xRange = ", self.xRange )

        self.x0, self.y0 = minN
        self.x1, self.y1 = maxN
        self.atlamayaGoreNoktalariGetir()
        self.analysisBtn.setDisabled(False)

    def sinirinKotlariniGetir(self):
        cevre = self.poly.length*100000
        print("cevre: ", cevre)
        samples = int(cevre/(self.atlama*(2/3)))
        print("samples: ", samples)
        if samples > 400:
            samples = 400
        # self.coords
        # sorguList, sorgu, syc  = [], "", 0
        # if len(self.noktalar) > 400:
        #     kacarKacar = 400
        # else:
        #     kacarKacar = len(self.noktalar)

        # for nokta in self.noktalar:
        #     sorgu+=nokta+"|"
        #     syc+=1
        #     if syc == kacarKacar or ((len(sorguList)) != 0 and (len(self.noktalar) - len(sorguList)*kacarKacar) == syc):
        #         sorguList.append(sorgu)
        #         sorgu, syc = "", 0
        # latlon = lat, lon
        # self.coords.append(latlon)
        koordinatlar = ""

        for koordinat in self.coords:
            koordinatlar += str(koordinat[1])+","+str(koordinat[0])+"|"
        koordinatlar = koordinatlar[:-1]
        self.sinirElevList, self.sorguKoordinatlari, pastTime = getHPoly(koordinatlar,samples)

    def atlamayaGoreNoktalariGetir(self):
        if self.kmlFilePath == "":
            return
        xLer = []
        yLer = []
        for i in range(0, int(self.xDistance_), self.atlama):
            xN = self.x0 + ((self.xRange*i)/self.xDistance_)
            xLer.append(xN)
        xLer.append(self.x1)
        for i in range(0, int(self.yDistance_), self.atlama):
            yN = self.y0 + ((self.yRange*i)/self.yDistance_)
            yLer.append(yN)
        yLer.append(self.y1)
        syc = 0
        
        pxLer = []
        self.noktalar = []
        for yn in xLer:
            for xn in yLer:
                syc +=1
                px = Point(xn, yn)
                nokta = xn, yn
                if px.within(self.poly):
                    self.noktalar.append(str(nokta[1])+","+str(nokta[0]))
                    # noktalar.append(encodePoints([[nokta[1], nokta[0]]]))
                    # print(str(nokta[1])+","+str(nokta[0]))
                    # print(encodePoints([[nokta[1], nokta[0]]]))

                    pxLer.append(px)
        self.olusacakNoktaLE.setText(str(len(self.noktalar)))

    def alanysisEt(self):
        self.sinirinKotlariniGetir()
        if self.kmlFilePath == "":
            return
        sorguList, sorgu, syc  = [], "", 0
        if len(self.noktalar) > 400:
            kacarKacar = 400
        else:
            kacarKacar = len(self.noktalar)
        # self.noktalar.append(str(nokta[1])+","+str(nokta[0]))
        # self.sinirElevList, self.sorguKoordinatlari, pastTime = getHPoly(koordinatlar,samples)
        # lat, lng = location["lat"], location["lng"]
        # sorguKoordinatlari.append((lat,lng))


        for nokta in self.noktalar:
            sorgu+=nokta+"|"
            syc+=1
            if syc == kacarKacar or ((len(sorguList)) != 0 and (len(self.noktalar) - len(sorguList)*kacarKacar) == syc):
                sorguList.append(sorgu)
                sorgu, syc = "", 0

        pastTimes = []
        elevLer = []
        self.pointsDict = {}
        # print(sorgu[:-1])




        for sorgu in sorguList:
            sorgu = sorgu[:-1]
            elevList, pastTime = getHF(sorgu) #elevList, pastTime
            elevLer.extend(elevList)
            pastTimes.append(pastTime)

            for index , sorguPoint in enumerate(sorgu.split("|")):
                self.pointsDict[sorguPoint] = elevList[index]

        for index, sorKord in enumerate(self.sorguKoordinatlari):
            point = str(sorKord[1])+","+str(sorKord[0]) #burada ter olabilir
            self.pointsDict[point] = self.sinirElevList[index]
        # print(len(sorguList))
        # print(len(self.noktalar))
        # print(self.pointsDict)
        # print("sorgulanan nokta adeti: ", len(elevLer))
        # print("max(elevLer) = ", max(elevLer))
        # print("min(elevLer) = ", min(elevLer))
        # print("avarage(pastTimes): ", mean(pastTimes))
        # print("toplam geçen süre: ", sum(pastTimes))
        topElev = max(elevLer)
        minElev = min(elevLer)
        # for key in list(self.pointsDict.keys()):
        #     if self.pointsDict[key] == topElev:
        #         print(self.pointsDict[key], key)
        self.topPoint = [key for key in self.pointsDict.keys() if self.pointsDict[key] == topElev]
        self.bottomPoint = [key for key in self.pointsDict.keys() if self.pointsDict[key] == minElev]
        print("self.topPoint: ", self.topPoint)
        print("self.bottomPoint: ", self.bottomPoint)

        self.maxElevLBL.setText(f"En yüksek kot = {topElev}")
        self.minElevLBL.setText(f"En düşük kot = {minElev}")
        self.totalPastTimeLBL.setText(f"Toplam Geçen Süre = {sum(pastTimes)}")
        self.avaragePastTimesLBL.setText(f"Her sorgu için ortalama geçen süre = {mean(pastTimes)}")
        self.sumSorguLBL.setText(f"Toplam yapılan sorgu adeti = {len(sorguList)}")
        self.bottomPointCheckBox.setDisabled(False)
        self.topPointCheckBox.setDisabled(False)
        self.noktalarCheckBox.setDisabled(False)
        self.saveKmlBtn.setDisabled(False)
        self.esYukselTiOlustur()

    def atlamaUptade(self):
        self.atlama = self.pointsRangeSpinBox.value()
        print("self.atlama = ", self.atlama)
        self.atlamayaGoreNoktalariGetir()
    
    def esYukselTiOlustur(self):
        center = self.poly.centroid
        # print("center: ", center)
        xc, yc = center.y, center.x # merkez nokta
        # merkezin güneyindeki ve kuzeyindeki noktalar
        self.kuzeyPoints, self.guneyPoints = [], []
        for point in self.pointsDict.keys():
            xn, yn = point.split(",")
            xn, yn = float(xn), float(yn)
            if xn >= xc:
                self.kuzeyPoints.append(point)
            else:
                self.guneyPoints.append(point)
        ayniKotlarKuzeyDict = {}
        # aslında burada noktalar kuzey istikametinde sıralanmış oluyor.
        for point in self.kuzeyPoints:
            kot = round(self.pointsDict[point])
            kotKeys = list(ayniKotlarKuzeyDict.keys())
            if not kot in kotKeys:
                ayniKotlarKuzeyDict[kot] = [point]
            else:
                ayniKotlarKuzeyDict[kot].append(point)
        ayniKotlarGuneyDict = {}
        # aynı kotları kod adında bir key oluşturup o kotlarda bulunan noktaları o key'e atama işlemini yapar.
        self.ayniKotlarHepsiDict = {}
        for point in list(self.pointsDict.keys()):
            kot = round(self.pointsDict[point])
            kotKeys = list(self.ayniKotlarHepsiDict.keys())
            if not kot in kotKeys:
                self.ayniKotlarHepsiDict[kot] = [point]
            else:
                self.ayniKotlarHepsiDict[kot].append(point)
        
    
    
    
    def getDist(self, p1, p2):
        x1, y1 = p1
        x2, y2 = p2
        dist = (abs(x2- x1)**2 + abs(y2-y1)**2)**0.5
        return dist
    
    def sirala(self, points):
        siraliList = []
        eyn = points[0]
        # ilk nokta listeye eklenir.
        siraliList.append(eyn)
        points_ = points
        points_.remove(eyn)
        distDict = {}
        # burada aslında bütün noktalar ile kıyaslama şeklinde olmamalı da
        # noktalar kuzeyden güneye sıralandığında kuzeyinde veya güneyinde kalan 5 nokta alınacak olursa.

        while len(points_) != 0:
            for i, p1 in enumerate(points):
                mesafeler = []
                for p2 in points_:
                    # ilk noktanın diğer noktalara olan uzaklığı
                    # sonrasında en yakın noktanın diğer noktalara olan uzaklığı
                    mesafe = self.getDistance (eyn, p2)
                    if not (eyn, p2) in list(distDict.keys()) or not (p2, eyn) in list(distDict.keys()):
                        distDict[(eyn, p2)] = mesafe
                    mesafeler.append((mesafe, p2))
                dists = [m[0] for m in mesafeler]
                dists.sort()
                en_dist = dists[0]
                for m in mesafeler:
                    if m[0] == en_dist:
                        eyn = m[1] # en yakın nokta
                if not eyn in siraliList:
                    siraliList.append(eyn)
                points_.remove(eyn)
                print(len(points_))
        print(len(siraliList) == len(points))

        for i, v in enumerate(siraliList):
            try:
                p1, p2 = siraliList[i], siraliList[i+1]
                mesafe = distDict[(p1, p2)]
                fp1 = p1
                for point in points:
                    if (point, p2) in list(distDict.keys()):
                        n_mesafe = distDict[(point, p2)]
                    else:
                        n_mesafe = self.getDistance(point, p2)
                    if n_mesafe<mesafe:
                        fp1 = point
                siraliList.insert(siraliList.index(fp1), p2)
                siraliList.remove(p2)
                if i+1 == len(siraliList):
                    break
            except:
                continue

        print(siraliList)
        return siraliList

    def onlyWithin(self, points):
        resultPoints = []
        for point in points:
            xn, yn = point
            px = Point(xn, yn)
            if px.within(self.poly):
                resultPoints.append((xn, yn))
        return resultPoints
    def savePoints(self):
        # analiz et çalıştıysa çalışabilmeli
        kml = simplekml.Kml()
        noktaAnalysis = kml.newfolder(name = "Nokta Analiz")
        # self.pointsDict
        # noktalar.append(str(nokta[1])+","+str(nokta[0]))
        # coords_ = [(nokta.split(",")[::-1]) for nokta in self.noktalar]
        # self.sinirElevList, self.sorguKoordinatlari, pastTime = getHPoly(koordinatlar,samples)
        
        if self.noktalarCheckBox.isChecked():
            noktalar = noktaAnalysis.newfolder(name = "Noktalar")
            # kuzeyPointF = noktalar.newfolder(name= "kuzeydeki noktalar")
            # guneyPointF = noktalar.newfolder(name = "guneydeki noktalar")
            sinirKotlari = noktalar.newfolder(name="sınır kotları")
            for index, kot in enumerate(self.sinirElevList):
                if round(float(kot))%10 == 0:
                    pointName = str(round(kot))
                    coord = self.sorguKoordinatlari[index][::-1]
                    sinirKotlari.newpoint(name=pointName, coords = [coord])

            for kot in (self.ayniKotlarHepsiDict.keys()):
                # eş yükselti oluşturulabilmesi için en az 5 nokta olsun ve kotlarda 10'un katları olması gerekir.
                if len(self.ayniKotlarHepsiDict[kot]) >= 5 and kot%10 == 0:
                    kotF = noktalar.newfolder(name = kot)
                    lineList = []

                    for point in self.ayniKotlarHepsiDict[kot]:
                        coord = point.split(",")[::-1]
                        lineList.append((float(coord[0]), float(coord[1])))
                        pointName = str(round(self.pointsDict[point]))
                        # kotF.newpoint(name=pointName, coords=[coord])
                    lineList = self.sirala(lineList)
                    lineList = self.onlyWithin(lineList)
                    line = LineString(lineList)
                    kmlLine = kotF.newlinestring(name= "kot")
                    kmlLine.coords = lineList
                    kmlLine.altitudemode = simplekml.AltitudeMode.relativetoground
                    kmlLine.extrude = 1

            # for key in list(self.pointsDict.keys()):
            #     coord = key.split(",")[::-1]
            #     pointName = str(round(self.pointsDict[key]))
            #     noktalar.newpoint(name=pointName, coords=[coord])
            # for point in self.kuzeyPoints:
            #     coord = point.split(",")[::-1]
            #     pointName = str(round(self.pointsDict[point]))
            #     kuzeyPointF.newpoint(name=pointName, coords=[coord])
            # for point in self.guneyPoints:
            #     coord = point.split(",")[::-1]
            #     pointName = str(round(self.pointsDict[point]))
            #     guneyPointF.newpoint(name=pointName, coords=[coord])
        
        if self.topPointCheckBox.isChecked():
            hp = noktaAnalysis.newfolder(name = "en yüksek kot")
            pointName = f"en yüksek kot = {round(self.pointsDict[self.topPoint[0]])}"
            coord = self.topPoint[0].split(",")[::-1]
            hp.newpoint(name=pointName, coords = [coord])
        if self.bottomPointCheckBox.isChecked():
            lp = noktaAnalysis.newfolder(name = "en düşük kot")
            lp.newpoint(name=f"en düşük kot = {round(self.pointsDict[self.bottomPoint[0]])}", coords = [self.bottomPoint[0].split(",")[::-1]])
        
        kml.save(self.kmlSavePath)

    def saveBtnState(self):
        print("state değişti")
        if self.topPointCheckBox.isChecked() or self.bottomPointCheckBox.isChecked() or self.noktalarCheckBox.isChecked():
            self.saveKmlBtn.setDisabled(False)
        else:
            self.saveKmlBtn.setDisabled(True)
    
    def doSomething(self, abc):
        print("doSomething çalıştı")
        print(self.poly.wkt)
        os.system(self.kmlSavePath)
    def initUI(self):
        # self.savedKmlLinkLBL.setOpenExternalLinks(True)
        self.setWindowTitle("Alan Kot Analiz Programı - Mehmet YERLİ")
        self.savedKmlLinkLBL.mousePressEvent = self.doSomething
        self.openKmlBtn.clicked.connect(self.openFileNameDialog)
        self.saveKmlBtn.clicked.connect(self.saveFileDialog)
        self.pointsRangeSpinBox.valueChanged.connect(self.atlamaUptade)
        self.analysisBtn.clicked.connect(self.alanysisEt)
        self.bottomPointCheckBox.stateChanged.connect(self.saveBtnState)
        self.topPointCheckBox.stateChanged.connect(self.saveBtnState)
        self.noktalarCheckBox.stateChanged.connect(self.saveBtnState)
        self.bottomPointCheckBox.setDisabled(True)
        self.topPointCheckBox.setDisabled(True)
        self.noktalarCheckBox.setDisabled(True)
        self.saveKmlBtn.setDisabled(True)
        self.analysisBtn.setDisabled(True)
        self.show() # Show the GUI

        

    
app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()

# QtWidgets.QWidget


#### yapılacaklar 
# noktalar, en yüksek nokta, en düşük nokta bunları opsiyonel olarak kml şeklinde kaydedilebilinmeli
# sınırın üzerinde de sorgulama yapılmalı
# noktalar arası mesafe doğru değil
# google api kodunu bir metin dosyasından almalı
# eş yükselti eğrileri sıralı gitmeli ve moving average uygunlanmalı gibi


# https://maps.googleapis.com/maps/api/elevation/json?path=37.96234375623109,34.71331998587725|37.94172656099543,34.71136326326116|37.9378103419424,34.72619545437203|37.95959690895765,34.74105524157671|37.96369432949525,34.72886601331405|37.96234375623109,34.71331998587725&samples=30&key=AIzaSyCg-5rgvNpcF2ak_WS97_V0M1b4EuCwrJk

