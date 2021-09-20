import requests as req


class Line(object):
    def __init__(self, vozniRed):
        self.vozniRed = vozniRed
        self.startTime, self.arrivalTime = self.makeTimeData(self.vozniRed)
        self.lineInfo = self.__postLineData(self.__curateLineData(self.vozniRed))

    def __curateLineData(self, line):
        # example input:
        # 0|1632108000|1|LJUBLJANA AVTOBUSNA POSTAJA|788|Logatec Krpan|2021-09-20 05:20:00|2021-09-20
        # 06:07:00|0:47|3.60|999|0|1|2138;57629;33413;1;1;788;22;2021-09-20 05:20:00;3.60
        data = line.split("|")
        lineData = data[-1]

        print("data: " + str(lineData))

        if lineData != "":
            return lineData

    def __postLineData(self, lineData):
        url = "https://www.ap-ljubljana.si/_vozni_red/get_linija_info_0.php"
        response = req.post(url, data=lineData)
        return response.text

    def makeTimeData(self, text):
        dataList = text.split("|")
        startTime = dataList[6]
        arrivalTime = dataList[7]
        return startTime, arrivalTime

    def getStartTime(self):
        return self.startTime
    
    def getArrivalTime(self):
        return self.arrivalTime

class BusGetter():
    def __init__(self, vstopId, izstopId, date):
        self.vstopId = vstopId
        self.izstopId = izstopId
        self.date = date

    def getVozniRed(self):
        url = "https://www.ap-ljubljana.si/_vozni_red/get_vozni_red_0.php?VSTOP_ID=" + self.vstopId + "&IZSTOP_ID=" + self.izstopId + "&DATUM=" + self.date
        response = req.get(url)
        return response.text