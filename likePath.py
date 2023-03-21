doc = open("11.kml", encoding="utf8").read()

coordinates = [[i.strip() for i in coor.split(",")] for coor in doc.split(
    "<coordinates>")[1].split("</coordinates>")[0].strip().split(",0") if coor != ""]
print(len(coordinates))
syc = 0
cevre = 0
while True:
    try:
        p1 = coordinates[syc]
        p2 = coordinates[syc+1]
        x1, y1 = float(p1[0]) , float(p1[1])
        x2, y2 = float(p2[0]) , float(p2[1])
        mesafe = ((x2-x1)**2 + (y2-y1)**2)**0.5
        print(p1, p2, "=>> ", mesafe)
        cevre += mesafe
        syc += 1
    except Exception as ex:
        break
print(coordinates)
print(cevre*100000)
