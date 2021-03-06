import requests
import json
from bs4 import BeautifulSoup
import os
import time


class EasistentAuth():
    def __init__(self, usrname, password):
        self.username = usrname
        self.password = password

    def getNewToken(self):
        loginData = {"uporabnik": self.username, "geslo": self.password}
        s = requests.Session()
        start_time = time.time()
        login = s.post("https://www.easistent.com/p/ajax_prijava", data = loginData)
        end_time = time.time()
        print("getNewToken login time: " + str(end_time - start_time))

        if json.loads(login.text)["status"] != "ok":
            return "Napačno uporabniško ime ali geslo! Poskusite znova!", ""

        else:
            start_time = time.time()
            src = s.get("https://www.easistent.com").text
            end_time = time.time()
            print("getNewToken src time: " + str(end_time - start_time))
            soup = BeautifulSoup(src, "html.parser")

            access_token = soup.find("meta", attrs = {"name": "access-token"})
            child_id = soup.find("meta", attrs = {"name": "x-child-id"})

            return access_token["content"], child_id["content"]

class EasistentClient():
    def __init__(self, access_token, child_id):
        self.session = requests.Session()
        self.headers = {
            "accept": "application/json, text/javascript, */*; q=0.01",
			"accept-encoding": "gzip, deflate, br",
			"accept-language": "sl,en;q=0.9,en-GB;q=0.8,en-US;q=0.7,cy;q=0.6",
			"authorization": str(access_token),
			"referer": "https://www.easistent.com/webapp",
			"sec-fetch-dest": "empty",
			"sec-fetch-mode": "cors",
			"sec-fetch-site": "same-origin",
			"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36 Edg/85.0.564.44",
			"x-child-id": str(child_id),
			"x-client-platform": "web",
			"x-client-version": "13",
			"x-requested-with": "XMLHttpRequest"
        }

    def getSchedule(self, mon, sun):
        mon = mon.strftime("%Y-%m-%d")
        sun = sun.strftime("%Y-%m-%d")
        #print(f"monday: {mon}")
        #print(f"sunday: {sun}")
        start_time = time.time()
        rurl = f"https://www.easistent.com/m/timetable/weekly?from={mon}&to={sun}"
        r = self.session.get(rurl, headers=self.headers)
        end_time = time.time()
        print("getSchedule time: " + str(end_time - start_time))
        try:
            if json.loads(r.text)["error"]:
                return "Invalid token/child id"

        except:
            return json.loads(r.text)
