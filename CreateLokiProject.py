#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
import json
from time import sleep
import re
from ArticutAPI import Articut
from requests import post

BASEPATH = os.path.dirname(os.path.abspath(__file__))

url = "https://api.droidtown.co/Loki/Call/" #LokiCall URL
userDICT = json.load(open("{}/account.info".format(BASEPATH), encoding="utf-8"))
username = userDICT["username"]
apikey   = userDICT["articut_key"]
datePat = re.compile("_\d\d\d\d-\d\d-\d\d")
articut = Articut(username, apikey, version="v267")


def createProject(projNameSTR):
    """
    自動產生 Loki 裡面的 project
    """

    payload = {
        "username": userDICT["username"], #Loki 的帳號
        "func": "create_project",
        "data": {
            "name": projNameSTR, #專案名稱
            "version": "v267",
        }
    }

    count = 0
    limit = 3
    while True:
        try:
            response = post(url, json=payload).json()
            if response["status"]:
                return response
            else:
                count += 1
                sleep(1)
                if count >= limit:
                    return {"status": False, "msg": str(e)}
        except Exception as e:
            count += 1
            sleep(1)
            if count >= limit:
                return {"status": False, "msg": str(e)}


def getProjectNamePinyin(inputSTR):
    count = 0
    limit = 3
    while True:
        try:
            pinyinResultDICT = articut.parse(inputSTR, level="lv3", pinyin="HANYU")
            if pinyinResultDICT["status"]:
                pinyin = "".join(pinyinResultDICT["utterance"]).replace(" ", "").replace("/", "")
                return {"status": True, "result": pinyin}
            else:
                count += 1
                sleep(1)
                if count >= limit:
                    return {"status": False, "msg": "Connection failed."}

        except Exception as e:
            count += 1
            sleep(1)
            if count >= limit:
                return {"status": False, "msg": str(e)}

if __name__ == "__main__":

    # 開啟所有原文檔案，已取得裁判書中文 title
    NameLIST = os.listdir("{}/lawCaseData/臺灣臺東地方法院_刑事_原文/".format(BASEPATH))
    print(NameLIST)

    if not os.path.exists("{}/lawCaseData/tryAgain".format(BASEPATH)):
        os.mkdir("{}/lawCaseData/tryAgain".format(BASEPATH), mode=0o777)

    #把下面寫成 function

    projectDICT = {}
    projectLoadAgain = []
    for name_s in NameLIST:
        if name_s.startswith("."):
            pass
        else:
            projNameSTR = name_s.replace(".json", "")
            projNameSTR = datePat.sub("", projNameSTR)
            pinyinSTR = getProjectNamePinyin(projNameSTR)["result"].replace(",", "_")
            response = createProject("{}".format(pinyinSTR))
            print(response)
            try:
                projectDICT[name_s] = {
                    "project_name": "{}".format(pinyinSTR),
                    "loki_key": response["loki_key"]
                }
            except:
                projectLoadAgain.append(name_s)

    with open("{}/lawCaseData/projectDICT.json".format(BASEPATH), "w", encoding="UTF-8") as f:
        json.dump(projectDICT, f, ensure_ascii=False, indent=3)

    with open("{}/lawCaseData/tryAgain/projectLoadAgainLIST.json".format(BASEPATH), "w", encoding="UTF-8") as f:
        json.dump(projectLoadAgain, f, ensure_ascii=False, indent=3)


    ## 如果已經有產生了每個 project 的名稱和對應 loki key 則直接讀入
    projectDICT = json.load(open("{}/lawCaseData/projectDICT.json".format(BASEPATH), encoding="UTF-8"))
