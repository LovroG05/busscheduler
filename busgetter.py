from flask.json import jsonify
import requests as req
import time


class Line(object):
    def __init__(self, vozniRed):
        self.vozniRed = vozniRed
        self.startTime, self.arrivalTime = self.makeTimeData(self.vozniRed)
        self.ping = 0
        self.lineInfo = ""
        #self.lineInfo = self.__postLineData(self.__curateLineData(self.vozniRed))

    def getPing(self):
        return self.ping
        
    def getStartTime(self):
        return self.startTime

    def getArrivalTime(self):
        return self.arrivalTime

    def curateLineData(self, line):
        data = line.split("|")
        lineData = data[-1]

        if lineData != "":
            return lineData

    def postLineData(self):
        url = "https://www.ap-ljubljana.si/_vozni_red/get_linija_info_0.php"
        obj = {"flags": self.curateLineData(self.vozniRed)}
        start_time = time.time()
        response = req.post(url, data=obj)
        end_time = time.time()
        ping_time = end_time - start_time
        self.ping = ping_time
        self.lineInfo = response.text

    def getTime(self, _time):
        obj = time.strptime(_time, "%Y-%m-%d %H:%M:%S")
        return obj
    

    def makeTimeData(self, text):
        dataList = text.split("|")
        startTime = self.getTime(dataList[6])
        arrivalTime = self.getTime(dataList[7])
        return startTime, arrivalTime

    def serialize(self):
        return {
            "vozniRed": self.vozniRed,
            "startTime": self.startTime,
            "arrivalTime": self.arrivalTime,
            "lineInfo": self.lineInfo
        }

class Misc():
    def serializeBusStations(self, stations):
        serializedStations = []
        for station in stations:
            if station != "":
                station = station.split(":")
                station = station[1]
                station = station.split("|")
                station_id = station[0]
                station_name = station[1]
                station_obj = {"lineId": station_id, "lineName": station_name}
                serializedStations.append(station_obj)

        return jsonify(serializedStations)


    def getBusStations(self):
        url = "https://www.ap-ljubljana.si/_vozni_red/get_postajalisca_vsa_v2.php"
        start_time = time.time()
        response = req.get(url)
        end_time = time.time()
        print("getBusStations ping time: " + str(end_time - start_time))
        text = str(response.text)
        #print("text: " + text)
        stations = text.split("\n")
        serializedStations = self.serializeBusStations(stations)
        return serializedStations
        


class BusGetter():
    def __init__(self, vstopId, izstopId, date):
        self.vstopId = vstopId
        self.izstopId = izstopId
        self.date = date

    def getVozniRed(self):
        url = "https://www.ap-ljubljana.si/_vozni_red/get_vozni_red_0.php?VSTOP_ID=" + str(self.vstopId) + "&IZSTOP_ID=" + str(self.izstopId) + "&DATUM=" + str(self.date)
        start_time = time.time()
        response = req.get(url)
        end_time = time.time()
        print("getVozniRed ping time: " + str(end_time - start_time))
        return response.text
