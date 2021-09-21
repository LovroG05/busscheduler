from requests.api import get
from busgetter import BusGetter, Line, Misc
import time
import datetime
from flask import Flask, jsonify, request
import easistent
import os
from dotenv import load_dotenv

load_dotenv()

WEEKDAY_TABLE = ["Pon", "Tor", "Sre", "Čet", "Pet", "Sob", "Ned"]

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
                14: 241023}

TIME_TABLE = {
        241008 : {"from": "07: 30", "to": "08: 15"}, 
        241026: {"from": "08: 20", "to": "09: 05"}, 
        241029: {"from": "09: 10", "to": "09: 55"},
        241032: {"from": "10: 00", "to": "10: 45"}, 
        241147: {"from": "10: 45", "to": "11: 05"}, 
        241035: {"from": "11: 05", "to": "11: 50"},
        241038: {"from": "11: 55", "to": "12: 40"},
        241041: {"from": "12: 45", "to": "13: 30"}, 
        241044: {"from": "13: 35", "to": "14: 20"}, 
        241047: {"from": "14: 25", "to": "15: 10"},
        241247: {"from": "15: 10", "to": "15: 30"}, 
        241011: {"from": "15: 30", "to": "16: 15"}, 
        241014: {"from": "16: 20", "to": "17: 05"}, 
        241017: {"from": "17: 10", "to": "17: 55"}, 
        241020: {"from": "18: 00", "to": "18: 45"}, 
        241023: {"from": "18: 50", "to": "19: 35"}
    }

TIME_MARGIN = datetime.timedelta(minutes=20)
USRNAME = os.getenv("USRNAME")
PASSWD = os.getenv("PASSWD")

app = Flask(__name__)

def getLatestArrival(date):
    eAuth = easistent.EasistentAuth(USRNAME, PASSWD)
    access_token, child_id = eAuth.getNewToken()

    eClient = easistent.EasistentClient(access_token, child_id)
    schedule = eClient.getSchedule()

    schoolHourEvents = schedule["school_hour_events"]

    hoursOnDate = []
    for hour in schoolHourEvents:
        if hour["time"]["date"] == date:
            hoursOnDate.append(hour)

    startTimeStr = hoursOnDate[0]["time"]["from_id"]


     
    """ 
    print(f"starting time: {startTimeStr}")
    todayDatetime = datetime.datetime.now()
    todayStr = todayDatetime.strftime("%Y-%m-%d")
    tStr = todayStr + " " + startTimeStr + ":00"
    startTime = datetime.datetime.strptime(tStr, "%Y-%m-%d %H:%M:%S")
    startTime = startTime - TIME_MARGIN
    print(f"latest arrival time: {startTime}")
    return startTime """



@app.route("/api/v1/getlines", methods=["GET"])
def api_get_lines():
    # args: start_station, end_station, date
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

    LATEST_ARRIVAL_TIME_OBJ = getLatestArrival(DATE)
    LATEST_ARRIVAL_TIME = LATEST_ARRIVAL_TIME_OBJ.strftime("%H:%M")
    
    WEEKDAY = LATEST_ARRIVAL_TIME_OBJ.today().weekday()

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