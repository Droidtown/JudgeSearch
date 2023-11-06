#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
import sys
import json
from BuildModel import addUtterance
from pprint import pprint

BASEPATH = os.path.dirname(os.path.abspath(__file__))


if __name__ == "__main__":

    ## 開好一個資料夾 tryAgain 收集需要再自動輸入 project name 到 Loki 的內容
    oldroundSTR = "firstRound"
    newroundSTR = "secondRound"
    if not os.path.exists("{}/lawCaseData/tryAgain/{}".format(BASEPATH, newroundSTR)):
        os.mkdir("{}/lawCaseData/tryAgain/{}".format(BASEPATH, newroundSTR), mode=0o777)

    ## 讀入所有需要重新自動加入 Loki 的內容
    tryAgainAddUtteranceNameLIST = os.listdir("{}/lawCaseData/tryAgain/{}".format(BASEPATH, oldroundSTR))
    print(tryAgainAddUtteranceNameLIST)

    AddUtteranceLIST = []
    for name_s in tryAgainAddUtteranceNameLIST:
        if name_s.startswith("tryAgainParse_addUtterance_"):
            profileLIST = json.load(open("{}/lawCaseData/tryAgain/firstRound/{}".format(BASEPATH, name_s), encoding="UTF-8"))
            AddUtteranceLIST = AddUtteranceLIST + profileLIST
    pprint(AddUtteranceLIST)


    ## 讀取projectDICT，取得 loki_key 的檔案
    projectDICT = json.load(open("{}/lawCaseData/projectDICT.json".format(BASEPATH), encoding="UTF-8"))

    ## 重新加入句子
    tryAgainParseLIST = []
    for value in projectDICT.values():
        for i in range(len(AddUtteranceLIST)):
            if value["project_name"] == AddUtteranceLIST[i]["projectName"]:
                print(AddUtteranceLIST[i]["projectName"])
                print(value["project_name"])
                print(AddUtteranceLIST[i]["newUtteranceLIST"])
                status, response = addUtterance(AddUtteranceLIST[i]["newIntentSTR"], AddUtteranceLIST[i]["newUtteranceLIST"], value["loki_key"], AddUtteranceLIST[i]["projectName"])
                if status:
                    pass
                else:
                    tryAgainParseLIST.append(response)

    ## 把還是有問題的句子存起來，等一下可以重新加入
    with open("{}/lawCaseData/tryAgain/{}/tryAgainParse_addUtterance.json".format(BASEPATH, newroundSTR), "a+", encoding="UTF-8") as f:
        json.dump(tryAgainParseLIST, f, ensure_ascii=False, indent=4)

