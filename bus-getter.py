import requests as req

LJUBLJANA_STATION_ID = "1"
LOGATEC_KRPAN_STATION_ID = "788"

def getVozniRed(vstopId, izstopId, date):
    url = "https://www.ap-ljubljana.si/_vozni_red/get_vozni_red_0.php?VSTOP_ID=" + vstopId + "&IZSTOP_ID=" + izstopId + "&DATUM=" + date
    response = req.get(url)
    return response.text()

def curateLineData(VozniRed):

    # TODO
    return lineData

def postLineData(lineData):
    url = "https://www.ap-ljubljana.si/_vozni_red/get_linija_info_0.php"
    response = req.post(url, data=lineData)
    return response.text()