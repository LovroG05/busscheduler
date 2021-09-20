from requests.api import get
from busgetter import BusGetter, Line
import time

LJUBLJANA_STATION_ID = "1"
LOGATEC_KRPAN_STATION_ID = "788"

WEEKDAY_TABLE = ["Pon", "Tor", "Sre", "Čet", "Pet", "Sob", "Ned"]

TODAY = "2021-09-20"
LATEST_ARRIVAL_TIME = TODAY + " 22:23:00"

LATEST_ARRIVAL_TIME_OBJ = time.strptime(LATEST_ARRIVAL_TIME, "%Y-%m-%d %H:%M:%S")
WEEKDAY = LATEST_ARRIVAL_TIME_OBJ[6]

print("Weekday: %s" % WEEKDAY_TABLE[WEEKDAY])


Bus = BusGetter(LJUBLJANA_STATION_ID, LOGATEC_KRPAN_STATION_ID, TODAY)
vozniRed = Bus.getVozniRed()

vozniRed = vozniRed.split("\n")
linesList = []
for i in vozniRed:
    if i != "":
        linesList.append(Line(i))

validStartLinesList = []

for i in linesList:
    startTime = time.mktime(i.getStartTime())
    timenow2 = time.time()
    seconds = startTime - timenow2
    if seconds > 0:
        validStartLinesList.append(i)

fullyValidLinesList = []

for i in validStartLinesList:
    arrivalTime = time.mktime(i.getArrivalTime())
    latestArrival = time.mktime(time.strptime(LATEST_ARRIVAL_TIME,  "%Y-%m-%d %H:%M:%S"))
    seconds = latestArrival - arrivalTime
    if seconds > 0:
        fullyValidLinesList.append(i)


print("VALID LINES TO ARRIVE BEFORE %s:" % LATEST_ARRIVAL_TIME)
for line in fullyValidLinesList:
    print(f"LINE START: %s\nLINE END: %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S", line.getStartTime()), time.strftime("%Y-%m-%d %H:%M:%S", line.getArrivalTime())))

