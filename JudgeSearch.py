#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import importlib
import json
import re

from glob import glob
from multiprocessing import Pool
from pathlib import Path, os
from pprint import pprint
from time import sleep, time
import sys

from ArticutAPI import Articut
datePat = re.compile("_\d\d\d\d-\d\d-\d\d")


execLokiFuncLIST = []

BASEPATH = os.path.dirname(os.path.abspath(__file__))
try:
    #from dev_99_su4_2.dev_99_su4_2 import execLoki as execLoki99su42
    for modulePath in glob("projects/*/*.py"):
        moduleNameSTR = Path(modulePath).stem.replace("_", "")
        globals()[moduleNameSTR] = getattr(importlib.import_module(modulePath.replace(".py", "").replace("/", ".")), "execLoki")
        execLokiFuncLIST.append([Path(modulePath).stem, globals()[moduleNameSTR]])
except:
    #from .dev_99_su4_2.dev_99_su4_2 import execLoki as execLoki99su42
    for modulePath in glob("projects/*/*.py"):
        if modulePath.endswith("__init__.py"):
            continue
        moduleNameSTR = Path(modulePath).stem
        dirLIST = os.listdir("/Users/robinlin/Documents/Py39/JudgeSearch/projects")
        for dirname in dirLIST:
            if dirname == ".DS_Store":
                continue
            else:
                sys.path.append(f"{BASEPATH}/projects/{dirname}")
        test = "." + modulePath.replace(".py", "").replace("/", ".")
        globals()[moduleNameSTR] = getattr(importlib.import_module("xying2shi4cai2dying4_100_jyao1su4_3"), "execLoki")
        execLokiFuncLIST.append([moduleNameSTR.replace("execLoki", ""), globals()[moduleNameSTR]])

    print(execLokiFuncLIST)




if "eclair" in os.path.expanduser("~"):
    articut = Articut(url="http://127.0.0.1:50266")
else:
    userDICT = json.load(open("{}/account.info".format(BASEPATH), encoding="utf-8"))
    username = userDICT["username"]
    apikey   = userDICT["articut_key"]
    articut = Articut(username, apikey, version="v267")

refDICT = {}
tagPAT = re.compile("<[^>]+>")

########################################################################
#                           Multiprocessing                            #
########################################################################

def getResultDICT(BASEPATH, orginalFileFolder):
    """
    取得放結果的 resultDICT
    output 樣子會是
    {裁判書拼音： {'judgement_file_name': 裁判書中文名稱}

    例如：
    {'xying2shi4pan4juue2_100_su4_147': {'judgement_file_name': '刑事判決_100,訴,147_2011-06-02.json'},
     'xying2shi4pan4juue2_100_su4_294': {'judgement_file_name': '刑事判決_100,訴,294_2012-06-05.json'},}

    """
    NameLIST = os.listdir("{}/lawCaseData/{}/".format(BASEPATH, orginalFileFolder))

    resultDICT = {}
    for name_s in NameLIST:
        if name_s.startswith("."):
            pass
        else:
            nameSTR = name_s.replace(".json", "")
            nameSTR = datePat.sub("", nameSTR)
            pinyinSTR = getProjectNamePinyin(nameSTR)["result"].replace(",", "_")
            resultDICT[pinyinSTR] = {"judgement_file_name": name_s}

    return resultDICT

def resultCallback(processResultDICT):
    #print(processResultDICT)
    try:
        resultDICT[processResultDICT["loki_project"]]["result"] = processResultDICT["result"]
    except Exception as e:
        print(e)

def run(processID, pinyinLIST, judLIST):
    """
    並執行 execLoki 的內容，以便取得所有分數
    """
    #print("#", processID)
    #print(execLokiFuncLIST[processID][0])

    ### 計算每一篇的分數
    print(matchPinyin(pinyinLIST, execLokiFuncLIST[processID][0]))
    print(execLokiFuncLIST[processID][1](judLIST, filterLIST=matchPinyin(pinyinLIST, execLokiFuncLIST[processID][0])))
    lokiResultDICT = execLokiFuncLIST[processID][1](judLIST,
                                                    refDICT=refDICT,
                                                    splitLIST=[],
                                                    filterLIST=matchPinyin(pinyinLIST, execLokiFuncLIST[processID][0]))
    print(lokiResultDICT)
    processResultDICT = {"loki_project": execLokiFuncLIST[processID][0],
                         "result": sum(lokiResultDICT[execLokiFuncLIST[processID][0]])}
    return processResultDICT

########################################################################
#                               Search                                 #
########################################################################

def text2LIST(lv2DICT):
    '''
    Converting string into a list of sentences.
    '''
    utteranceLIST = []
    verbINDEX = articut.getVerbStemLIST(lv2DICT)

    for i in range(len(verbINDEX)):
        if verbINDEX[i]:
            utteranceSTR = lv2DICT["result_pos"][i]
            utteranceSTR = tagPAT.sub("", utteranceSTR)
            utteranceLIST.append(utteranceSTR)

    return utteranceLIST


def preprocessing(profileLIST):
    """
    前處理裁判書原文中的 judgement
    處理內容
    - 看 judgement 的格式，如果非 string 就整併成 string
    - judgement 裡面如果有 dict 的格式，就把 dict 拿掉，dict 是判決書中的表格
    - 把全型空格 (\u3000)、換行、空格替換掉
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

def getPinyin(lv2DICT, inputSTR): #新版
    """
    找到 inputLIST 中每一句的第一個動詞，然後轉成 pinyin
    """
    pinyinLIST = []
    #print(inputSTR)
    try:
        # 中文斷詞
        count = 0
        limit = 3
        while True:
            try:
                #lv2DICT = articut.parse(inputSTR, level='lv2')
                lv3DICT = articut.parse(inputSTR, level='lv3', pinyin='HANYU')

                #if lv2DICT["status"] and lv3DICT["status"]:
                if lv3DICT["status"]:
                    verbINDEX = articut.getVerbStemLIST(lv2DICT)

                    for i in range(len(verbINDEX)):
                        if verbINDEX[i]:
                            # verbINDEX[0][0][0] 第一個是第幾句(就是 i), 第二個 0 是把 list 拿掉，第三個零是 lv3 verbINDEX 中的第一個數字
                            verbIndex = lv2DICT["result_pos"][i][:verbINDEX[i][0][0]].count("</")
                            pinyinSTR = lv3DICT["utterance"][i].split("/")[verbIndex].replace(" ", "").replace("/", "")
                            pinyinLIST.append(pinyinSTR)

                    pinyinLIST = list(set(pinyinLIST))

                    return pinyinLIST
                else:
                    count += 1
                    sleep(1)
                    if count >= limit:
                        #print("Articut Error more than three times")
                        return []
            except:
                #print("Articut Error")
                return []
    except:
        #print("Articut Error")
        return []




def matchPinyin(pinyinLIST, pathSTR):
    print(pathSTR)
    """
    這個 function 會拿剛剛找到的 pinyinLIST 然後 return 一個 list 可以當作 filterLIST 用
    """
    # 比對 intent
    intentLIST = os.listdir("{}/projects/{}/intent/".format(BASEPATH, pathSTR))
    resultLIST = []
    for pinyin_s in pinyinLIST:
        for intent_s in intentLIST:
            intentSTR = intent_s.replace("Loki_", "").replace(".py", "")
            if pinyin_s in intentSTR:
                resultLIST.append(intentSTR)

    resultLIST = list(set(resultLIST))
    print(resultLIST)

    return resultLIST

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

########################################################################

if __name__ == "__main__":

    ### 測試

    ### 讀檔

    # 如果已經有現成的資料，可以直接用 inputSTR
    inputSTR = """臺灣苗栗地方法院刑事判決105年度訴字第164號公訴人臺灣苗栗地方法院檢察署檢察官被告謝文男指定辯護人本院公設辯護人蔡文亮上列被告因違反毒品危害防制條例案件，經檢察官提起公訴（105年度毒偵字第305號），又被告於準備程序中就被訴事實為有罪之陳述，經本院合議庭裁定由受命法官獨任行簡式審判程序後，檢察官聲請改依協商程序而為判決，本院判決如下：主文謝文男施用第一級毒品，處有期徒刑拾月。犯罪事實及理由一、本件犯罪事實及證據：除證據部分，補充：被告謝文男於本院準備程序中之自白，餘均引用起訴書之記載（如附件）。二、本件經檢察官與被告於審判外達成協商之合意且被告已認罪，其合意內容為：被告願受科刑範圍為有期徒刑10月。經查，上開協商合意並無刑事訴訟法第455條之4第1項所列情形之一，檢察官聲請改依協商程序而為判決，本院爰不經言詞辯論，於協商合意範圍內為協商判決，合予敘明。三、應適用之法條：刑事訴訟法第273條之1第1項、第455條之2第1項、第455條之4第2項、第455條之8、第454條第2項，毒品危害防制條例第10條第1項。四、附記事項：被告施用第一級毒品海洛因所使用之針筒，為其所有，供犯上開犯罪所用之物，惟未扣案，且被告供稱：使用的針筒已經被我丟掉了等語（見毒偵卷第27頁、本院卷第21頁反面），復無證據證明尚屬存在。衡諸上開器具非違禁物或其他依法應沒收之物，爰不予宣告沒收。五、本判決除有刑事訴訟法第455條之4第1項第1款、第2款、第4款、第6款、第7款所定情形之一，或違反同條第2項規定者外，不得上訴。如有前述例外得上訴之情形，又不服本件判決，得自判決送達後10日內，向本院提出上訴書狀併附理由，上訴於第二審法院。中華民國105年5月26日刑事第二庭法官陳雅菡以上正本證明與原本無異。書記官林義盛中華民國105年5月26日附錄本案論罪科刑法條：毒品危害防制條例第10條施用第一級毒品者，處6月以上5年以下有期徒刑。施用第二級毒品者，處3年以下有期徒刑。"""
    inputSTR = """臺灣臺東地方法院刑事裁定111年度易字第56號公訴人臺灣臺東地方檢察署檢察官被告彭立雄本件被告彭立雄因誣告案件，經檢察官依通常程序起訴，而被告自白犯罪，依刑事訴訟法第449條第1項規定，本院認為宜由受命法官獨任逕以簡易判決處刑，特此裁定。中華民國111年4月25日刑事第二庭審判長法官蔡立群以上正本證明與原本無異。"""
    ## 如果需要前處理，就可以讀取其他原文資料，然後再前處理，以下以「臺灣苗栗地方法院_刑事_原文/刑事裁定_110,訴,414_2022-10-12.json 為例
    #profileLIST = json.load(open("{}/lawCaseData/臺灣苗栗地方法院_刑事_原文/刑事裁定_110,訴,414_2022-10-12.json".format(BASEPATH), encoding="UTF-8"))
    #inputSTR = preprocessing(profileLIST)

    ### 取得新裁判書的 articut lv2 結果
    lv2DICT = articut.parse(inputSTR, level="lv2")

    ### 使用 articut lv2 結果 斷句
    judLIST = text2LIST(lv2DICT)

    ### 取得這篇的拼音
    pinyinLIST = getPinyin(lv2DICT, inputSTR)

    ### 準備放結果的 resultDICT
    orginalFileFolder = "臺灣臺東地方法院_刑事_原文" #建模用的裁判書原文資料夾名稱
    resultDICT = getResultDICT(BASEPATH, orginalFileFolder)

    ### 平行運算預備
    pool = Pool(processes=os.cpu_count())
    #pool = Pool(processes=2)

    ### 計算每一篇的分數
    for i in range(len(execLokiFuncLIST)):
        pool.apply_async(run, (i, pinyinLIST, judLIST), callback=resultCallback)

    pool.close()
    pool.join()

    ### 把分數整理成一個 dict; 分數越高，代表和該篇裁判書越像
    #pprint(resultDICT)

    ### 確定 resultDICT 裡面都有 "result" 這個 key
    resultCheckedDICT = {}
    for key, value in resultDICT.items():
        if "result" in value:
            resultCheckedDICT[key] = value
        else:
            print("這一篇沒有 result")
            print(value["judgement_file_name"])


    ### 按照分數把 resultDICT 排好，然後 print 出結果
    sortedLIST = sorted(resultCheckedDICT.items(), key=lambda x:x[1]["result"], reverse=True)


    resLIST = []
    for res_tup in sortedLIST:
        print(res_tup)
        resSTR = "積分：{} 比較裁判書：{}".format(res_tup[1]["result"], res_tup[1]["judgement_file_name"])
        resLIST.append(resSTR)

    pprint(resLIST)
    print(len(resLIST))












