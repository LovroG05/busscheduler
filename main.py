from requests.api import get
from busgetter import BusGetter, Line, Misc
import time
import datetime
from flask import Flask, jsonify, request
import easistent
import os
from dotenv import load_dotenv
import json

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
    14: 241023
}

TIME_TABLE = {
    241008: {"from": "07:30", "to": "08:15"}, 
    241026: {"from": "08:20", "to": "09:05"}, 
    241029: {"from": "09:10", "to": "09:55"},
    241032: {"from": "10:00", "to": "10:45"}, 
    241147: {"from": "10:45", "to": "11:05"}, 
    241035: {"from": "11:05", "to": "11:50"},
    241038: {"from": "11:55", "to": "12:40"},
    241041: {"from": "12:45", "to": "13:30"}, 
    241044: {"from": "13:35", "to": "14:20"}, 
    241047: {"from": "14:25", "to": "15:10"},
    241247: {"from": "15:10", "to": "15:30"}, 
    241011: {"from": "15:30", "to": "16:15"}, 
    241014: {"from": "16:20", "to": "17:05"}, 
    241017: {"from": "17:10", "to": "17:55"}, 
    241020: {"from": "18:00", "to": "18:45"},
    241023: {"from": "18:50", "to": "19:35"}
}


USRNAME = os.getenv("USRNAME")
PASSWD = os.getenv("PASSWD")

app = Flask(__name__)

def modEventTime(time):
    # removes space from time
    time = time.split(" ")
    return time[0]

def getFromAndToId(_time):
    # returns from_id and to_id from TIME_TABLE by start time of event
    from_time = _time["from"]
    to_time = _time["to"]
    from_time = modEventTime(from_time)
    to_time = modEventTime(to_time)

    new_to_time = datetime.datetime.strptime(from_time, "%H:%M") + datetime.timedelta(minutes=45)
    new_from_time = datetime.datetime.strptime(to_time, "%H:%M") - datetime.timedelta(minutes=45)

    from_id = list(TIME_TABLE.keys())[list(TIME_TABLE.values()).index({"from": from_time, "to": new_to_time.strftime("%H:%M")})]
    to_id = list(TIME_TABLE.keys())[list(TIME_TABLE.values()).index({"from": new_from_time.strftime("%H:%M"), "to": to_time})]

    return from_id, to_id

def getStartTime(date):
    # returns start time of school from TIME_TABLE
    eAuth = easistent.EasistentAuth(USRNAME, PASSWD)
    access_token, child_id = eAuth.getNewToken()

    eClient = easistent.EasistentClient(access_token, child_id)
    schedule = eClient.getSchedule()

    schoolHourEvents = schedule["school_hour_events"]
    events = []
    if schedule["events"] != []:
        events =schedule["events"]
        for event in events:
            """ event = json.loads(event) """
            idFrom, idTo = getFromAndToId(event["time"])
            event["time"] = {"from_id": idFrom, "to_id": idTo, "date": event["date"]}

            schoolHourEvents.append(event)

    schoolHourEvents.sort(key=lambda x: x["time"]["from_id"])

    hoursOnDate = []
    for hour in schoolHourEvents:
        if hour["time"]["date"] == date:
            hoursOnDate.append(hour)

    startTimeId = hoursOnDate[0]["time"]["from_id"]
    startTimeStr = TIME_TABLE[startTimeId]["from"]

    return startTimeStr

def getEndTime(date):
    # returns end time of school from TIME_TABLE
    eAuth = easistent.EasistentAuth(USRNAME, PASSWD)
    access_token, child_id = eAuth.getNewToken()

    eClient = easistent.EasistentClient(access_token, child_id)
    schedule = eClient.getSchedule()

    schoolHourEvents = schedule["school_hour_events"]
    events = []
    if schedule["events"] != []:
        events =schedule["events"]
        for event in events:
            """ event = json.loads(event) """
            idFrom, idTo = getFromAndToId(event["time"])
            event["time"] = {"from_id": idFrom, "to_id": idTo, "date": event["date"]}

            schoolHourEvents.append(event)

    schoolHourEvents.sort(key=lambda x: x["time"]["from_id"], reverse=True)

    hoursOnDate = []
    for hour in schoolHourEvents:
        if hour["time"]["date"] == date:
            hoursOnDate.append(hour)

    endTimeId = hoursOnDate[-1]["time"]["to_id"]
    endTimeStr = TIME_TABLE[endTimeId]["to"]

    return endTimeStr

def getLatestArrival(date, dir, timeMargin):
    if dir == "to_school":
        timeStr = getStartTime(date)
    elif dir == "from_school":
        timeStr = getEndTime(date)
    else:
        return "ERROR invalid direction"

    print(f"starting/finish time: {timeStr}")
    todayStr = date
    tStr = todayStr + " " + timeStr + ":00"
    startTime = datetime.datetime.strptime(tStr, "%Y-%m-%d %H:%M:%S")
    startTime = startTime - timeMargin
    print(f"latest arrival time: {startTime}")
    return startTime 

def getArrivalTimeNoMargin(date, dir):
    if dir == "to_school":
        timeStr = getStartTime(date)
    elif dir == "from_school":
        timeStr = getEndTime(date)
    else:
        return "ERROR invalid direction"

    todayStr = date
    tStr = todayStr + " " + timeStr + ":00"
    startTime = datetime.datetime.strptime(tStr, "%Y-%m-%d %H:%M:%S")
    return startTime 

def getEarlyArrival(date, dir, timeMargin):
    startTime = getArrivalTimeNoMargin(date, dir)
    startTime = startTime - timeMargin
    print(f"earliest arrival time: %s" % startTime.strftime("%Y-%m-%d %H:%M:%S"))
    return startTime

@app.route("/api/v1/getlines", methods=["GET"])
def api_get_lines():
    # args: start_station, end_station, date, dir, time_margin, early_time_margin
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
    if "dir" in request.args:
        DIR = request.args["dir"]
    else:
        return "ERROR: no dir provided"
    if "time_margin" in request.args:
        TIME_MARGIN = datetime.timedelta(minutes=int(request.args["time_margin"]))
    else:
        TIME_MARGIN = datetime.timedelta(minutes=20)
    if "early_time_margin" in request.args:
        EARLY_TIME_MARGIN = datetime.timedelta(minutes=int(request.args["early_time_margin"]))
    else:
        EARLY_TIME_MARGIN = datetime.timedelta(minutes=40)

    LATEST_ARRIVAL_TIME_OBJ = getLatestArrival(DATE, DIR, TIME_MARGIN)
    LATEST_ARRIVAL_TIME = LATEST_ARRIVAL_TIME_OBJ.strftime("%H:%M")
    
    EARLY_ARRIVAL_TIME_OBJ = getEarlyArrival(DATE, DIR, EARLY_TIME_MARGIN)
    EARLY_ARRIVAL_TIME = EARLY_ARRIVAL_TIME_OBJ.strftime("%H:%M")
    
    """  WEEKDAY = LATEST_ARRIVAL_TIME_OBJ.today().weekday() """

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

    """ print(validStartLinesList1) """


    # get lines that arrive in time
    validStartLinesList2 = []
    for i in validStartLinesList1:
        arrivalTime = time.mktime(i.getArrivalTime())
        """ print(f"arrival time: %s" % time.strftime("%Y-%m-%d %H:%M:%S", i.getStartTime())) """
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



@app.route("/api/v1/getstations", methods=["GET"])
def api_get_stations():
    misc = Misc()
    stations = misc.getBusStations()
    return stations

app.run()