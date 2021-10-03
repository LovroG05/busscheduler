import time
import datetime
import easistent
import busgetter
import workdays


class TimeLineUtils():
    def __init__(self):
        self.TIME_TABLE = {
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

    def modEventTime(self, time):
        # removes space from time
        time = time.split(" ")
        return time[0]

    def getFromAndToId(self, _time):
        # returns from_id and to_id from TIME_TABLE by start time of event
        from_time = _time["from"]
        to_time = _time["to"]
        from_time = self.modEventTime(from_time)
        to_time = self.modEventTime(to_time)

        new_to_time = datetime.datetime.strptime(from_time, "%H:%M") + datetime.timedelta(minutes=45)
        new_from_time = datetime.datetime.strptime(to_time, "%H:%M") - datetime.timedelta(minutes=45)

        from_id = list(self.TIME_TABLE.keys())[list(self.TIME_TABLE.values()).index({"from": from_time, "to": new_to_time.strftime("%H:%M")})]
        to_id = list(self.TIME_TABLE.keys())[list(self.TIME_TABLE.values()).index({"from": new_from_time.strftime("%H:%M"), "to": to_time})]

        return from_id, to_id

    def getMonSun(self, date):
        # returns mon-fri from date
        theday = datetime.datetime.strptime(date, "%Y-%m-%d")
        weekday = theday.isoweekday()
        start = theday - datetime.timedelta(days=weekday)
        dates = [start + datetime.timedelta(days=d) for d in range(7)]

        monday = dates[1]
        sunday = dates[-1] + datetime.timedelta(days=1) 
        print(f"monday: {monday}")
        print(f"sunday: {sunday}")

        return monday, sunday
        

    def getStartTime(self, date, eClient):
        # returns start time of school from TIME_TABLE
        monday, sunday = self.getMonSun(date)
        schedule = eClient.getSchedule(monday, sunday)

        # print(f"schedule: {schedule}")

        schoolHourEvents = schedule["school_hour_events"]
        events = []
        if schedule["events"] != []:
            events = schedule["events"]
            for event in events:
                """ event = json.loads(event) """
                idFrom, idTo = self.getFromAndToId(event["time"])
                event["time"] = {"from_id": idFrom, "to_id": idTo, "date": event["date"]}

                schoolHourEvents.append(event)

        for event in schoolHourEvents:
            if event["hour_special_type"] == "cancelled":
                schoolHourEvents.remove(event)

        actualEventHours = []
        for event in schoolHourEvents:
            print(f"eventDate: {event['time']['date']}")
            print(f"date: {date}")
            if event["time"]["date"] == date:
                actualEventHours.append(event)

        print(f"actualEventHours: {actualEventHours}")
        actualEventHours.sort(key=lambda x: x["time"]["from_id"])

        timeList = []
        for event in actualEventHours:
            tstr = self.TIME_TABLE[event["time"]["from_id"]]["from"]
            timeList.append(datetime.datetime.strptime(tstr, "%H:%M"))

        if len(timeList) == 0:
            return ""

        startTime = min(timeList)
        startTimeStr = startTime.strftime("%H:%M")

        print(f"startTimeStr: {startTimeStr}")

        return startTimeStr

    def getEndTime(self, date, eClient):
        # returns end time of school from TIME_TABLE
        monday, sunday = self.getMonSun(date)
        schedule = eClient.getSchedule(monday, sunday)

        schoolHourEvents = schedule["school_hour_events"]
        events = []
        if schedule["events"] != []:
            events =schedule["events"]
            for event in events:
                """ event = json.loads(event) """
                idFrom, idTo = self.getFromAndToId(event["time"])
                event["time"] = {"from_id": idFrom, "to_id": idTo, "date": event["date"]}

                schoolHourEvents.append(event)

        for event in schoolHourEvents:
            if event["hour_special_type"] == "cancelled":
                schoolHourEvents.remove(event)

        actualEventHours = []
        for event in schoolHourEvents:
            print(f"eventDate: {event['time']['date']}")
            print(f"date: {date}")
            if event["time"]["date"] == date:
                actualEventHours.append(event)

        print(f"actualEventHours: {actualEventHours}")
        actualEventHours.sort(key=lambda x: x["time"]["from_id"])


        timeList = []
        for event in actualEventHours:
            tstr = self.TIME_TABLE[event["time"]["to_id"]]["to"]
            timeList.append(datetime.datetime.strptime(tstr, "%H:%M"))

        if len(timeList) == 0:
            return ""

        endTime = max(timeList)
        endTimeStr = endTime.strftime("%H:%M")
        print(f"endTimeStr: {endTimeStr}")

        return endTimeStr

    def getLatestArrival(self, date, dir, timeMargin, eClient):
        if dir == "to_school":
            timeStr = self.getStartTime(date, eClient)
        elif dir == "from_school":
            timeStr = self.getEndTime(date, eClient)
        else:
            return "ERROR invalid direction"

        if timeStr == "":
            return ""

        print(f"starting/finish time: {timeStr}")
        todayStr = date
        tStr = todayStr + " " + timeStr + ":00"
        startTime = datetime.datetime.strptime(tStr, "%Y-%m-%d %H:%M:%S")
        if dir == "to_school":
            startTime = startTime - timeMargin
        elif dir == "from_school":
            startTime = startTime + timeMargin
        print(f"latest arrival time: {startTime}")
        return startTime 

    def getArrivalTimeNoMargin(self, date, dir, eClient):
        if dir == "to_school":
            timeStr = self.getStartTime(date, eClient)
        elif dir == "from_school":
            timeStr = self.getEndTime(date, eClient)
        else:
            return "ERROR invalid direction"

        if timeStr == "":
            return ""

        todayStr = date
        tStr = todayStr + " " + timeStr + ":00"
        startTime = datetime.datetime.strptime(tStr, "%Y-%m-%d %H:%M:%S")
        return startTime 

    def getEarlyArrival(self, date, dir, timeMargin, eClient):
        startTime = self.getArrivalTimeNoMargin(date, dir, eClient)
        if startTime == "":
            return ""
        if dir == "to_school":
            startTime = startTime - timeMargin
        elif dir == "from_school":
            startTime = startTime + timeMargin
        print(f"earliest arrival time: %s" % startTime.strftime("%Y-%m-%d %H:%M:%S"))
        return startTime

    def getEarlyStartTime(self, date, early_time_margin, eClient):
        timeStr = self.getEndTime(date, eClient)
        if timeStr == "":
            return ""
        todayStr = date
        tStr = todayStr + " " + timeStr
        startTime = datetime.datetime.strptime(tStr, "%Y-%m-%d %H:%M")
        startTime = startTime + early_time_margin
        return startTime