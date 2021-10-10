from requests.api import get
from busgetter import BusGetter, Line, Misc
import time
import datetime
from flask import Flask, jsonify, request
import easistent
import os
#from dotenv import load_dotenv
import json
import timelineutils

#load_dotenv()

""" WEEKDAY_TABLE = ["Pon", "Tor", "Sre", "Čet", "Pet", "Sob", "Ned"]

HOUR_ID_TABLE = {
    1: 241008, 
    2: 241026, 
    3: 241029, 
    4: 241032, 
    "malca1": 241147, 
    5: 241035, 
    6: 241038, 
    7: 241041, 
    8: 241044, 
    "malca2": 241047, 
    9: 241247, 
    10: 241011, 
    11: 241014, 
    12: 241017, 
    13: 241020, 
    14: 241023
}
 """


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



    print("\nVALID LINES TO ARRIVE BEFORE %s:" % LATEST_ARRIVAL_TIME)
    for line in validStartLinesList3:
        print(f"LINE START: %s\nLINE END: %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S", line.getStartTime()), time.strftime("%Y-%m-%d %H:%M:%S", line.getArrivalTime())))
    

    # serialize lines to json
    serializedLines = []
    for i in validStartLinesList3:
        serializedLines.append(i.serialize())

    return jsonify({"lines": serializedLines})

# http GET request for bus lines coming FROM school
# args: start_station, end_station, date, latest_arrival_required, latest_arrival, early_time_margin
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
    if "latest_arrival_required" in request.args:
        if request.args["latest_arrival_required"] == "true":
            LATEST_ARRIVAL_REQUIRED = True
            if "latest_arrival" in request.args:
                LATEST_ARRIVAL_TIME = request.args["latest_arrival"]
            else:
                return "ERROR: no latest_arrival provided yet latest_arrival_required is 'true'"
        else:
            LATEAST_ARRIVAL_REQUIRED = False
    else:
        LATEST_ARRIVAL_REQUIRED = False
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

    if LATEST_ARRIVAL_REQUIRED:
        LATEST_ARRIVAL_TIME = DATE + " " + LATEST_ARRIVAL_TIME + ":00"

        LATEST_ARRIVAL_TIME_OBJ = datetime.datetime.strptime(LATEST_ARRIVAL_TIME, "%Y-%m-%d %H:%M:%S")
    
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
    print(f"early start time: {EARLY_START_TIME}")
    for i in linesList:
        lineDepartureTime = time.mktime(i.getStartTime())
        earlyStartTime = time.mktime(EARLY_START_TIME_OBJ.timetuple())
        seconds = lineDepartureTime - earlyStartTime
        if seconds > 0:
            validStartLinesList1.append(i)

    # get lines that arrive in time if required TODO
    if LATEST_ARRIVAL_REQUIRED:
        validStartLinesList2 = []
        for i in validStartLinesList1:
            arrivalTime = time.mktime(i.getArrivalTime())
            latestArrival = time.mktime(LATEST_ARRIVAL_TIME_OBJ.timetuple())
            seconds = latestArrival - arrivalTime
            if seconds > 0:
                validStartLinesList2.append(i)

        print("\nVALID LINES TO ARRIVE BEFORE %s:" % LATEST_ARRIVAL_TIME)
        for line in validStartLinesList2:
            print(f"LINE START: %s\nLINE END: %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S", line.getStartTime()), time.strftime("%Y-%m-%d %H:%M:%S", line.getArrivalTime())))
        

        # serialize lines to json
        serializedLines = []
        for i in validStartLinesList2:
            serializedLines.append(i.serialize())

        return jsonify({"lines": serializedLines})

    else:
        """ print("\nVALID LINES TO ARRIVE BEFORE %s:" % LATEST_ARRIVAL_TIME) """
        print("\n VALID LINES:")
        for line in validStartLinesList1:
            print(f"LINE START: %s\nLINE END: %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S", line.getStartTime()), time.strftime("%Y-%m-%d %H:%M:%S", line.getArrivalTime())))
        

        # serialize lines to json
        serializedLines = []
        for i in validStartLinesList1:
            serializedLines.append(i.serialize())

        return jsonify({"lines": serializedLines})

@app.route("/api/v1/getstations", methods=["GET"])
def api_get_stations():
    misc = Misc()
    stations = misc.getBusStations()
    return stations

if __name__ == "__main__":
    app.run(debug=True)