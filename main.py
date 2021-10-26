from requests.api import get
from busgetter import BusGetter, Line, Misc
import time
import datetime
from flask import Flask, jsonify, request
import easistent
import os
import json
import timelineutils
import threading


app = Flask(__name__)

# http GET request for getting bus lines for going TO school
# args: start_station, end_station, date, time_margin, early_time_margin
@app.route("/api/v1/getlinestoschool", methods=["GET"])
def api_get_lines_to():
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
    if "time_margin" in request.args:
        TIME_MARGIN = datetime.timedelta(minutes=int(request.args["time_margin"]))
    else:
        TIME_MARGIN = datetime.timedelta(minutes=20)
    if "early_time_margin" in request.args:
        EARLY_TIME_MARGIN = datetime.timedelta(minutes=int(request.args["early_time_margin"]))
    else:
        EARLY_TIME_MARGIN = datetime.timedelta(minutes=40)
    if "username" in request.args:
        USERNAME = request.args["username"]
    else:
        return "ERROR: no username provided"
    if "password" in request.args:
        PASSWORD = request.args["password"]
    else:
        return "ERROR: no password provided"

    DIR = "to_school"

    eAuth = easistent.EasistentAuth(USERNAME, PASSWORD)
    access_token, child_id = eAuth.getNewToken()
    eClient = easistent.EasistentClient(access_token, child_id)

    timeLineUtils = timelineutils.TimeLineUtils()

    LATEST_ARRIVAL_TIME_OBJ = timeLineUtils.getLatestArrival(DATE, DIR, TIME_MARGIN, eClient)
    if LATEST_ARRIVAL_TIME_OBJ == "":
        return {"error": "no lessons/non all day events", "lines": "{}"}
    LATEST_ARRIVAL_TIME = LATEST_ARRIVAL_TIME_OBJ.strftime("%H:%M")
    
    EARLY_ARRIVAL_TIME_OBJ = timeLineUtils.getEarlyArrival(DATE, DIR, EARLY_TIME_MARGIN, eClient)
    if EARLY_ARRIVAL_TIME_OBJ == "":
        return {"error": "no lessons/non all day events", "lines": "{}"}
    EARLY_ARRIVAL_TIME = EARLY_ARRIVAL_TIME_OBJ.strftime("%H:%M")

    Bus = BusGetter(START_STATION_ID, END_STATION_ID, DATE)
    vozniRed = Bus.getVozniRed()

    # vozni red to Line list
    vozniRed = vozniRed.split("\n")
    linesList = []
    for i in vozniRed:
        if i != "":
            linesList.append(Line(i))

    
    # get lines that havent already passed
    validStartLinesList1 = []
    for i in linesList:
        startTime = time.mktime(i.getStartTime())
        timenow2 = time.time()
        seconds = startTime - timenow2
        if seconds > 0:
            validStartLinesList1.append(i)

    # get lines that arrive in time
    validStartLinesList2 = []
    for i in validStartLinesList1:
        arrivalTime = time.mktime(i.getArrivalTime())
        latestArrival = time.mktime(LATEST_ARRIVAL_TIME_OBJ.timetuple())
        seconds = latestArrival - arrivalTime
        if seconds > 0:
            validStartLinesList2.append(i)

    # get lines that dont arrive to early
    validStartLinesList3 = []
    for i in validStartLinesList2:
        arrivalTime = time.mktime(i.getArrivalTime())
        earlyArrival = time.mktime(EARLY_ARRIVAL_TIME_OBJ.timetuple())
        seconds = arrivalTime - earlyArrival
        if seconds > 0:
            validStartLinesList3.append(i)

    thread_list = []
    for i in validStartLinesList1:
        thread = threading.Thread(target=i.postLineData)
        thread_list.append(thread)

    for thread in thread_list:
        thread.start()

    for thread in thread_list:
        thread.join()

    # serialize lines to json
    serializedLines = []
    for i in validStartLinesList3:
        print("line ping: " + str(i.getPing()))
        serializedLines.append(i.serialize())

    return jsonify({"lines": serializedLines})

# http GET request for bus lines coming FROM school
# args: start_station, end_station, date, early_time_margin
@app.route("/api/v1/getlinesfromschool", methods=["GET"])
def api_get_lines_from():
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
    if "early_time_margin" in request.args:
        EARLY_TIME_MARGIN = datetime.timedelta(minutes=int(request.args["early_time_margin"]))
    else:
        EARLY_TIME_MARGIN = datetime.timedelta(minutes=20)
    if "username" in request.args:
        USERNAME = request.args["username"]
    else:
        return "ERROR: no username provided"
    if "password" in request.args:
        PASSWORD = request.args["password"]
    else:
        return "ERROR: no password provided"

    DIR = "from_school"

    eAuth = easistent.EasistentAuth(USERNAME, PASSWORD)
    access_token, child_id = eAuth.getNewToken()
    eClient = easistent.EasistentClient(access_token, child_id)

    timeLineUtils = timelineutils.TimeLineUtils()
    
    EARLY_START_TIME_OBJ = timeLineUtils.getEarlyStartTime(DATE, EARLY_TIME_MARGIN, eClient)
    if EARLY_START_TIME_OBJ == "":
        return {"error": "no lessons/non all day events", "lines": "{}"}
    EARLY_START_TIME = EARLY_START_TIME_OBJ.strftime("%H:%M")

    Bus = BusGetter(START_STATION_ID, END_STATION_ID, DATE)
    vozniRed = Bus.getVozniRed()

    # vozni red to Line list
    vozniRed = vozniRed.split("\n")
    linesList = []
    for i in vozniRed:
        if i != "":
            linesList.append(Line(i))

    
    # get lines that wont have passed
    validStartLinesList1 = []
    #print(f"early start time: {EARLY_START_TIME}")
    for i in linesList:
        lineDepartureTime = time.mktime(i.getStartTime())
        earlyStartTime = time.mktime(EARLY_START_TIME_OBJ.timetuple())
        seconds = lineDepartureTime - earlyStartTime
        if seconds > 0:
            validStartLinesList1.append(i)

    thread_list = []
    for i in validStartLinesList1:
        thread = threading.Thread(target=i.postLineData)
        thread_list.append(thread)

    for thread in thread_list:
        thread.start()

    for thread in thread_list:
        thread.join()


    # serialize lines to json
    serializedLines = []
    for i in validStartLinesList1:
        print("line ping: " + str(i.getPing()))
        serializedLines.append(i.serialize())

        return jsonify({"lines": serializedLines})

@app.route("/api/v1/getstations", methods=["GET"])
def api_get_stations():
    misc = Misc()
    stations = misc.getBusStations()
    return stations

@app.route("/api/v2/benchmark", methods=["GET"])
def api_benchmark():
    return {"time_received": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

if __name__ == "__main__":
    app.run(debug=True)