#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
import sys
import json
from math import ceil
from pprint import pprint
from requests import post
from ArticutAPI import Articut
from time import sleep, time
import re
from collections import defaultdict

BASEPATH = os.path.dirname(os.path.abspath(__file__))

userDICT = json.load(open("{}/account.info".format(BASEPATH), encoding="utf-8"))
username = userDICT["username"] #這裡填入您在 https://api.droidtown.co 使用的帳號 email。若使用空字串，則預設使用每小時 2000 字的公用額度。
apikey   = userDICT["articut_key"] #這裡填入您在 https://api.droidtown.co 登入後取得的 api Key。若使用空字串，則預設使用每小時 2000 字的公用額度。
articut = Articut(username, apikey, version="v267")
tagPAT = re.compile("<[^>]+>")
datePat = re.compile("_\d\d\d\d-\d\d-\d\d")

url = "https://api.droidtown.co/Loki/Call/" #LokiCall URL


def createIntent(intentSTR, lokiKeySTR, projectNameSTR):
    """
    自動新增 project 下 的 intent
    """
    payload = {
        "username" : userDICT["username"], #Loki 帳號
        "loki_key" : lokiKeySTR,           #Loki key
        "project": projectNameSTR,         #project 名稱
        "intent": intentSTR,               #intent 名稱
        "func": "create_intent",
        "data": {
            "type": "basic"
        }
    }

    response = post(url, json=payload).json()
    return response


def insertUtterance(intentSTR, utteranceLIST, lokiKeySTR, projectNameSTR):
    """
    自動輸入 intent 內的句子
    """

    payload = {
        "username" : userDICT["username"],   #Loki 帳號
        "loki_key" : lokiKeySTR,             #Loki key
        "project": projectNameSTR,           #project 名稱
        "intent": intentSTR,                 #intent 名稱
        "func": "insert_utterance",
        "data": {
            "utterance": utteranceLIST,      #想要輸入的句子，要以 list 方式輸入
            "checked_list": ["UserDefined", "ENTITY_classifier", "ENTITY_measurement", "ENTITY_person", "ENTITY_pronoun", "ENTITY_possessive", "ENTITY_noun", "ENTITY_nounHead", "ENTITY_nouny", "ENTITY_oov", "ENTITY_DetPhrase", "KNOWLEDGE_currency", "KNOWLEDGE_lawTW", "LOCATION", "RANGE_locality", "KNOWLEDGE_addTW", "KNOWLEDGE_place", "KNOWLEDGE_routeTW", "KNOWLEDGE_wikiData", "KNOWLEDGE_chemical", "IDIOM"]
        }
    }

    response = post(url, json=payload).json()
    return response

def addUtterance(newIntentSTR, newUtteranceLIST, lokiKeySTR, projectNameSTR):
    """
    自動新增意圖名稱和大量新增句子
    """
    try:
        count = 0
        limit = 3
        while True:
            #自動輸入 intent
            res = createIntent(newIntentSTR, lokiKeySTR, projectNameSTR)
            print("Create intent:")
            print(res)
            if not res["status"]:
                if res["msg"] != "Intent already exists.":
                    count += 1
                    sleep(1)
                    if count >= limit:
                        with open("{}/lawCaseData/tryAgain/firstRound/tryAgain_CreateIntent_{}.txt".format(BASEPATH, projectNameSTR), "a+", encoding="UTF-8") as f:
                            f.write("{}\n".format(newIntentSTR))
                        raise Exception(res.msg)
                else:
                    print(res)
                    break
            else:
                print(res)
                break

        count = 0
        limit = 3
        #把想要輸入的句子 20 句為一單位一起輸入到 Loki
        callIndex = ceil(len(newUtteranceLIST) / 20)
        for i in range(callIndex):
            addLIST = [s for s in newUtteranceLIST[i*20:(i+1)*20]]
            while True:
                #自動輸入 utterance
                res = insertUtterance(newIntentSTR, addLIST, lokiKeySTR, projectNameSTR)
                print("Insert utterance [{}]:".format(count))
                if not res["status"]:
                    if res["msg"] != "Utterance already exist.":
                        count += 1
                        sleep(1)
                        if count >= limit:
                            with open("{}/lawCaseData/tryAgain/firstRound/tryAgain_InsertUtterance_{}.txt".format(BASEPATH, projectNameSTR), "a+", encoding="UTF-8") as f:
                                f.write("{}\n".format("\n".join(addLIST)))
                            raise Exception(res.msg)
                    else:
                        print(res)
                        break
                else:
                    print(res)
                    break
        return True, {}

    except Exception as e:
        print("[Error] addUtterance: {}".format(e))
        tryAgain_addUtteranceDICT = {
            "projectName": projectNameSTR,
            "newIntentSTR":newIntentSTR,
            "newUtteranceLIST": newUtteranceLIST,
            "error_message": str(e),
        }

        return False, tryAgain_addUtteranceDICT

def getFirstVerbUtterance(lv2DICT, inputSTR): #新版
    """
    找到 inputLIST 中每一句的第一個動詞，然後轉成 pinyin
    """
    pinyinLIST = [] #收集拼音
    utteranceLIST = [] #收集句子 (utterance)
    tryAgainParseUtteranceLIST = [] #收集因故沒有完成轉拼音的內容

    count = 0
    limit = 3
    while True:
        try:
            #使用 Articut lv3 取得拼音
            lv3DICT = articut.parse(inputSTR, level='lv3', pinyin='HANYU')
            if lv3DICT["status"]:
                #取得inputSTR Articut 斷詞結果（lv2DICT) 的所有動詞和動詞的所在位置
                verbINDEX = articut.getVerbStemLIST(lv2DICT)

                #取得動詞拼音
                for i in range(len(verbINDEX)):
                    if verbINDEX[i]:
                        #verbINDEX[i][0][0]
                            #第i句 是第 i 句的所有動詞 [(636, 638, '違反'), (791, 792, '等')]
                            #第二個零是選擇這一句的第一個動詞 e.g., (636, 638, '違反')
                            #第三個零是 lv3 第一個動詞在 lv2 result_pos 內位置 e.g., 636
                        #verbSerialNUM 是在 lv2DICT 每一句的第幾個詞
                        verbSerialNUM = lv2DICT["result_pos"][i][:verbINDEX[i][0][0]].count("</")
                        utteranceSTR = lv2DICT["result_pos"][i]
                        utteranceSTR = tagPAT.sub("", utteranceSTR)
                        try:
                            pinyinSTR = lv3DICT["utterance"][i].split("/")[verbSerialNUM].replace(" ", "").replace("/", "")
                            pinyinLIST.append(pinyinSTR)
                            utteranceLIST.append(utteranceSTR)
                        except Exception as e:
                            #如果這個 utterance 沒有輸入成功，就把錯誤訊息和句子存起來
                            tryAgainParseDICT = {
                                "utterance": utteranceSTR,
                                "error_message": str(e),
                            }
                            tryAgainParseUtteranceLIST.append(tryAgainParseDICT)

                ## 將 pinyinLIST, utteranceLIST zip 起來之後，轉成 dictionary
                resDICT = defaultdict(list)
                for k, v in zip(pinyinLIST, utteranceLIST):
                    resDICT[k].append(v)

                resDICT = dict(resDICT)

                ## 去重複
                setResDICT = {}
                for key in resDICT:
                    value = list(set(resDICT[key]))
                    setResDICT[key] = value
                return {"status": True, "setResDICT": setResDICT, "tryAgainParseUtteranceLIST": tryAgainParseUtteranceLIST}
            else:
                count += 1
                sleep(1)
                if count >= limit:
                    return {"status": False}
        except:
            return {"status": False}



def buildLokiModel(resDICT, lokiKeySTR, projectNameSTR):
    """
    把句子自動輸入到 loki 中
    """
    tryAgainParseLIST = []
    for key, value in resDICT.items():
        status, response = addUtterance(key, value, lokiKeySTR, projectNameSTR)
        if status:
            print(status)
        else:
            tryAgainParseLIST.append(response)
    with open("{}/lawCaseData/tryAgain/firstRound/tryAgainParse_addUtterance_{}.json".format(BASEPATH, projectNameSTR), "a+", encoding="UTF-8") as f:
        json.dump(tryAgainParseLIST, f, ensure_ascii=False, indent=4)





if __name__ == "__main__":


    ## 開好一個叫做 projects 的檔案夾。之後可以來放每一篇裁判書的模型。一篇裁判書是系統中的一個 project
    if not os.path.exists("{}/projects".format(BASEPATH)):
        os.mkdir("{}/projects".format(BASEPATH), mode=0o777)

    ## 開好一個資料夾 tryAgain 收集需要再自動輸入 project name 到 Loki 的內容
    if not os.path.exists("{}/lawCaseData/tryAgain/firstRound".format(BASEPATH)):
        os.mkdir("{}/lawCaseData/tryAgain/firstRound".format(BASEPATH), mode=0o777)

    ## 產生了每個 project 的名稱和對應 loki key 則直接讀入
    projectDICT = json.load(open("{}/lawCaseData/projectDICT.json".format(BASEPATH), encoding="UTF-8"))

    #########################################################

    for projSTR in projectDICT:
        #print(projSTR)
        ### 讀入之前已經斷好詞的 articut LV2 的內容
        with open("{}/lawCaseData/臺灣臺東地方法院_刑事_Articut_v267/{}".format(BASEPATH, projSTR), encoding="UTF-8") as f:
            profileSTR = f.read()
        lv2DICT = json.loads(profileSTR)

        ### 取得 preprocess 好的結果
        preprocessedNameSTR = projSTR.replace(".json", "")
        with open("{}/lawCaseData/preprocessedData/{}.txt".format(BASEPATH, preprocessedNameSTR), encoding="UTF-8") as f:
            inputSTR = f.read()

        ### 將含有動詞的句子取出，然後存成 dictionary 的樣子
        resultDICT = getFirstVerbUtterance(lv2DICT, inputSTR)
        if resultDICT["status"]:
            ## 把需要再處理的句子另外儲存成一個 json 檔案
            with open("{}/lawCaseData/tryAgain/firstRound/tryAgainParse_utterance_{}.json".format(BASEPATH, projSTR), "a+", encoding="UTF-8") as f:
                json.dump(resultDICT["tryAgainParseUtteranceLIST"], f, ensure_ascii=False, indent=4)

            ### 自動輸入intent 和 句子
            buildLokiModel(resultDICT["setResDICT"], projectDICT[projSTR]["loki_key"], projectDICT[projSTR]["project_name"])

        else:
            ### 把需要再處理的句子另外儲存成一個 text 檔案
            with open("{}/lawCaseData/tryAgain/firstRound/TryToParseAgainJudgement.txt".format(BASEPATH), "a+", encoding="UTF-8") as f:
                f.write("{}\n".format(projSTR))








