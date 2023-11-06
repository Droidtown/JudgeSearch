#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
import json

BASEPATH = os.path.dirname(os.path.abspath(__file__))

def preprocessing(profileLIST):
    """
    前處理裁判書原文中的 judgement
    這邊裁判書原文中有的全形空格、換行和空格換掉
    """
    # 根據 judgement 裡面的型態，來做不同的措施所以可以把 judgement 裡面的內容變成 string
    if type(profileLIST["judgement"]) == list:
        # 確保 judLIST 中都是 string, 不會有 dict (註：會有 dict 是因為有的 list 中有表格)
        judLIST = [x for x in profileLIST["judgement"] if type(x) == str]
        judSTR = "".join(judLIST)
    else:
        judSTR = profileLIST["judgement"]

    # 把全形空格 (\u3000)、換行還有空格取代
    judSTR = judSTR.replace("\u3000", " ").replace("\r\n", "").replace("\n", "").replace(" ", "")

    return judSTR

if __name__ == "__main__":



    ## 開好一個叫做 lawCaseData 的檔案夾和 preprocessedData 的資料夾。可以拿來放前處理好的內容。
    print(BASEPATH)
    if not os.path.exists("{}/lawCaseData".format(BASEPATH)):
        os.mkdir("{}/lawCaseData".format(BASEPATH), mode=0o777)
    if not os.path.exists("{}/lawCaseData/preprocessedData".format(BASEPATH)):
        os.mkdir("{}/lawCaseData/preprocessedData".format(BASEPATH), mode=0o777)



    typeSTR = "臺灣臺東地方法院_刑事_原文" #此處放裁判書原文的檔名

    #fileNameLIST 是 lawCaseData 中所有檔案名稱
    fileNameLIST = os.listdir("{}/lawCaseData/{}".format(BASEPATH,typeSTR))

    for file_s in  fileNameLIST:
        # 讀取資料
        profileLIST = json.load(open("{}/lawCaseData/{}/{}".format(BASEPATH,typeSTR,file_s), encoding="UTF-8"))

        # 前處理資料
        preprocessedSTR = preprocessing(profileLIST)

        # 把前處理的內容存起來
        file_s = file_s.replace(".json", "")
        with open("{}/lawCaseData/preprocessedData/{}.txt".format(BASEPATH, file_s), "w", encoding="UTF-8") as f:
            f.write(preprocessedSTR)

