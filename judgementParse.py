#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
import json
from ArticutAPI import Articut
from time import sleep
BASEPATH = os.path.dirname(os.path.abspath(__file__))

userDICT = json.load(open("{}/account.info".format(BASEPATH), encoding="utf-8"))
username = userDICT["username"]
apikey   = userDICT["articut_key"]
articut = Articut(username, apikey, version="v267")

def judgementParse(profileSTR):
    """
    把前處理的句子使用 articut level 2 來取得斷詞結果
    斷好的結果之後可以拿來斷句，和拿來取得有動詞的句子
    """
    count = 0
    limit = 3
    while True:
        try:
            resultDICT = articut.parse(profileSTR, level="lv2")
            if resultDICT["status"]:
                return resultDICT
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

    ## 開好一個叫做 lawCaseData 的檔案夾和 一個可以拿來放斷詞好的資料夾。
    print(BASEPATH)
    orginalTextName = "臺灣臺東地方法院_刑事" #此處放裁判書來源名稱
    ArticutVersion = "v267" #此處放 Articut version

    if not os.path.exists("{}/lawCaseData".format(BASEPATH)):
        os.mkdir("{}/lawCaseData".format(BASEPATH), mode=0o777)
    if not os.path.exists("{}/lawCaseData/tryAgain".format(BASEPATH)):
        os.mkdir("{}/lawCaseData/tryAgain".format(BASEPATH), mode=0o777)
    if not os.path.exists("{}/lawCaseData/{}_Articut_{}".format(BASEPATH, orginalTextName, ArticutVersion)):
        os.mkdir("{}/lawCaseData/{}_Articut_{}".format(BASEPATH, orginalTextName, ArticutVersion), mode=0o777)


    ##讀取所有 前處理資料的內容
    #fileNameLIST 是 lawCaseData/preprocessedData 中所有前處理的檔案名稱
    fileNameLIST = os.listdir("{}/lawCaseData/preprocessedData".format(BASEPATH))


    for file_s in  fileNameLIST:
        if file_s.endswith(".txt"):
            print(file_s)

            # 讀取資料
            with open("{}/lawCaseData/preprocessedData/{}".format(BASEPATH,file_s), encoding="utf-8") as f:
                profileSTR = f.read()
            # 斷詞

            resultDICT = judgementParse(profileSTR)
            #print(resultDICT)

            if resultDICT["status"]:
                file_s = file_s.replace(".txt", "")
                with open("{}/lawCaseData/{}_Articut_{}/{}.json".format(BASEPATH, orginalTextName, ArticutVersion, file_s), "w", encoding="utf-8") as f:
                    json.dump(resultDICT, f, ensure_ascii=False, indent=3)
            else:
                with open("{}/lawCaseData/tryAgain/ArticutLv2TryAgain.txt".format(BASEPATH, orginalTextName, ArticutVersion, file_s), "w+", encoding="utf-8") as f:
                    f.write("{}\n".format(file_s))

