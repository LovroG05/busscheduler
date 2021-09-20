from requests.api import get
from busgetter import BusGetter, Line

LJUBLJANA_STATION_ID = "1"
LOGATEC_KRPAN_STATION_ID = "788"

Bus = BusGetter(LJUBLJANA_STATION_ID, LOGATEC_KRPAN_STATION_ID, "2021-09-20")
vozniRed = Bus.getVozniRed()

vozniRed = vozniRed.split("\n")
linesList = []
for i in vozniRed:
    if i != "":
        linesList.append(Line(i))



