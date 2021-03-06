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
        start_time = time.thread_time()
        url = "https://www.ap-ljubljana.si/_vozni_red/get_linija_info_0.php"
        obj = {"flags": self.curateLineData(self.vozniRed)}
        response = req.post(url, data=obj)
        self.lineInfo = response.text
        end_time = time.thread_time()
        ping_time = end_time - start_time
        self.ping = ping_time

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
                if station[0] == "0":
                    station = station[1]
                    station = station.split("|")
                    station_id = station[0]
                    station_name = station[1]
                    if station_id != "":
                        if station_name != "":
                            station_obj = {"lineId": station_id, "lineName": station_name}
                            serializedStations.append(station_obj)

        return jsonify(serializedStations)


    def getBusStations(self):
        url = "https://www.ap-ljubljana.si/_vozni_red/get_postajalisca_vsa_v2.php"
        response = req.get(url)
        text = str(response.text)
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
