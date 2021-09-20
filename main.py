from requests.api import get
from busgetter import BusGetter, Line, Misc
import time
import datetime
from flask import Flask, jsonify, request


WEEKDAY_TABLE = ["Pon", "Tor", "Sre", "Čet", "Pet", "Sob", "Ned"]


app = Flask(__name__)

@app.route("/api/v1/getlines", methods=["GET"])
def api_get_lines():
    # args: start_station, end_station, date, latest_arrival
    if "start_station" in request.args:
        START_STATION_ID = int(request.args["start_station"])
    else:
        START_STATION_ID = 1
    if "end_station" in request.args:
        END_STATION_ID = int(request.args["end_station"])
    else:
        return "ERROR: no end_station provided"
    if "date" in request.args:
        DATE = request.args["date"]
    else:
        DATE = datetime.datetime.now().strftime("%Y-%m-%d")
    if "latest_arrival" in request.args:
        LATEST_ARRIVAL_TIME = request.args["latest_arrival"]
    else: 
        LATEST_ARRIVAL_TIME = DATE + "23:59:59"

    LATEST_ARRIVAL_TIME_OBJ = time.strptime(LATEST_ARRIVAL_TIME, "%Y-%m-%d %H:%M:%S")
    WEEKDAY = LATEST_ARRIVAL_TIME_OBJ[6]

    Bus = BusGetter(START_STATION_ID, END_STATION_ID, DATE)
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

    serializedLines = []

    for i in fullyValidLinesList:
        serializedLines.append(i.serialize())

    return jsonify({"lines": serializedLines})



@app.route("/api/v1/getstations", methods=["GET"])
def api_get_stations():
    misc = Misc()
    stations = misc.getBusStations()
    return stations

app.run()