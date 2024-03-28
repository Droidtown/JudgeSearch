#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os

BASEPATH = os.path.dirname(os.path.abspath(__file__))

def stateEvaluation(folderNameSTR):
    """
    修改 INTENT.py 中所有 #write your code here 變成計算每一個 args 的樣子
    """
    for proj_s in os.listdir("{}/{}/".format(BASEPATH, folderNameSTR)):
        if proj_s.startswith("."):
            pass
        else:
            for intent_s in os.listdir("{}/{}/{}/intent/".format(BASEPATH, folderNameSTR, proj_s)):
                if intent_s.startswith("Loki_") and intent_s.endswith(".py"):
                    with open("{}/{}/{}/intent/{}".format(BASEPATH, folderNameSTR, proj_s, intent_s), encoding = "utf-8") as f:
                        content = f.read().replace("# write your code here", "resultDICT[\"{}\"].append(len([a for a in args if a != \"\"]))".format(proj_s)).replace("pass", "")
                    with open("{}/{}/{}/intent/{}".format(BASEPATH, folderNameSTR, proj_s, intent_s), "w", encoding = "utf-8") as f:
                        f.write(content)


def changeLokiResultOutput(folderNameSTR):
    """
    修改主程式 (e.g., xying2shi4pan4juue2_109_yi4_79.py) 中 lokiResultDICT = {} 修改為 lokiResultDICT = {判決書名稱:[]}(e.g., lokiResultDICT = {"xying2shi4pan4juue2_109_yi4_79":[]})
    """
    for proj_s in os.listdir("{}/{}/".format(BASEPATH, folderNameSTR)):
        if proj_s.startswith("."):
            pass
        else:
            print(proj_s)
            with open("{}/{}/{}/{}.py".format(BASEPATH, folderNameSTR, proj_s, proj_s), encoding = "utf-8") as f:
                content = f.read().replace("lokiResultDICT = {k: [] for k in refDICT}", f"lokiResultDICT = {{\"{proj_s}\":[]}}").replace("globals()[moduleNameSTR] = import_module(modulePathSTR)", "globals()[moduleNameSTR] = import_module(f\"projects.{Path(BASE_PATH).stem}.{modulePathSTR}\")")
            with open("{}/{}/{}/{}.py".format(BASEPATH, folderNameSTR, proj_s, proj_s), "w", encoding = "utf-8") as f:
                f.write(content)


def moreChancesforrunLoki(folderNameSTR):
    """
    如果 runLoki 因故執行失敗，可以有三次重來的機會
    """
    for proj_s in os.listdir("{}/{}/".format(BASEPATH, folderNameSTR)):
        if proj_s.startswith("."):
            pass
        else:
            with open("{}/{}/{}/{}.py".format(BASEPATH, folderNameSTR, proj_s, proj_s), encoding = "utf-8") as f:
                content = f.read().replace(
    """        # 依 INPUT_LIMIT 限制批次處理
        for i in range(0, math.ceil(len(inputLIST) / INPUT_LIMIT)):
            resultDICT = runLoki(inputLIST[i*INPUT_LIMIT:(i+1)*INPUT_LIMIT], filterLIST=filterLIST, refDICT=resultDICT)
            if "msg" in resultDICT:
                break
""",
    """        # 依 INPUT_LIMIT 限制批次處理
        count = 0
        limit = 3
        for i in range(0, math.ceil(len(inputLIST) / INPUT_LIMIT)):
            while True:
                resultDICT = runLoki(inputLIST[i*INPUT_LIMIT:(i+1)*INPUT_LIMIT], filterLIST=filterLIST, refDICT=resultDICT)
                if "msg" not in resultDICT:
                    break

                count += 1
                time.sleep(1)
                if count >= limit:
                    return {"status": False, "msg": resultDICT["msg"]}""")
            with open("{}/{}/{}/{}.py".format(BASEPATH, folderNameSTR, proj_s, proj_s), "w", encoding = "utf-8") as f:
                f.write(content)

def addImportTime(folderNameSTR):
    """
    加入 import time
    """
    for proj_s in os.listdir("{}/{}/".format(BASEPATH, folderNameSTR)):
        if proj_s.startswith("."):
            pass
        else:
            with open("{}/{}/{}/{}.py".format(BASEPATH, folderNameSTR, proj_s, proj_s), encoding = "utf-8") as f:
                content = f.read().replace(
    """import re""",
    """import re
import time""")
            with open("{}/{}/{}/{}.py".format(BASEPATH, folderNameSTR, proj_s, proj_s), "w", encoding = "utf-8") as f:
                f.write(content)


if __name__ == "__main__":

    folderNameSTR = "projects" #是放所有 projects 的資料夾
    stateEvaluation(folderNameSTR)
    changeLokiResultOutput(folderNameSTR)

    ### 如果需要把多給 Loki 幾次跑的機會，可以執行以下兩個 function
    moreChancesforrunLoki(folderNameSTR)
    addImportTime(folderNameSTR)
