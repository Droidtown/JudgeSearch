# 裁判書比對系統 demo 程式製作步驟說明

## 製作模型

**說明**

* 將要被比對的裁判書建立成為模型，以下步驟以一篇裁判書為例。
* 本次示範檔案僅會使用到原文中的 judgement 欄位，此欄位為裁判書全文。範例如下：

```python
 "judgement":"臺灣臺東地方法院刑事裁定　　　　　　　 100年度訴字第27號\r\n公　訴　人　臺灣臺東地方法院檢察署\r\n被　　　告　黃賓來\r\n本件被告所犯係死刑、無期徒刑、.\r\n以外之罪，其於準備程序中就被訴.\r\n知簡式審判程序之旨，並聽取公訴.\r\n訟法第273條之1第1項規定，.\r\n簡式審判程序，特此裁定。\r\n中　　華　　民　　國　 100.\r\n以上正本證明與原本無異。\r\n本件不得抗告。\r\n中　　華　　民　　國　 100."
```
 
* 在執行以下步驟時，請您先確認擁有以下檔案：
	* `lawCaseData` 資料夾：此資料夾內將會被放入 `preprocessedData `, `臺灣臺東地方法院_刑事_Articut_v267`,  `tryAgain `，還有 `臺灣臺東地方法院_刑事_原文`
	* `account.info` : 此檔案要放 Loki 的帳號 (註冊的 email) 以及 Articut key ，檔案內容形式如下：

	```python
	{
    	"username": "此處放 註冊卓騰的 email ",
    	"articut_key": "此處放 Aritcut key"
    } 
	```

* 以下資料夾會在執行程式時自動產生
   * `preprocessedData`: 前處理後所有裁判書會儲存在這個資料夾
   * `臺灣臺東地方法院_刑事_Articut_v267`: 所有斷完詞的裁判書會存在這個資料夾。其中`臺灣臺東地方法院_刑事` 和 `v267`（Articut version）可以根據您手上的資料做替換
	* `tryAgain`: 如果有需要再次斷詞或是重新自動加入 Loki 的句子會放在這個資料夾

**步驟**

Step 0: 請先確定有創建一個 `lawCaseData` 的資料夾，這個資料夾和其他 `JudgeSearch.py` 等程式是放在同一個資料夾。之後有想要跑的原文資料夾 (e.g., `臺灣臺東地方法院_刑事_原文` 資料節 )可以放在 `lawCaseData`  中。此範例程式使用的原文可以參考 [臺灣臺東地方法院_刑事_原文] (https://drive.google.com/drive/folders/1hnAxfc0LNBQutzUPmxQp-08L1MHXpnMJ?usp=sharing)
 
Step 1: 前處理裁判書全文。將原始文檔中的全形空格、半形空格、換行符號替換掉。

   * 程式檔案請參考 `preprocessing.py`
   * 取得裁判書中 judgement 的欄位後，先判斷 judgement 的型態 (e.g., 是為 list, or string)，如果 judgement 是 list 則 join 為 string。如果 judgement 中含有 dictionary，則把 dictionary 刪除。
   * 取代 judgement string 中所有的全形空格為空格。再把換行符號和空格取代為 `""`

Step 2: 取得前處理過的文章的 Articut Level 2 結果。

   * 程式檔案請參考 `judgementParse.py`
   * 此結果之後會拿來當作斷句、取得所有動詞句子的依據

Step 3: 自動化創建 Loki project 到 Loki 網站。

   * 程式檔案請參考 `CreateLokiProject.py`
   * Project 名稱是將判決 ID (e.g., 刑事判決_99,訴,2) 利用 Articut Lv3 轉成拼音

Step 4: 建立 Loki 模型

1) 讀入 preprocess 好的結果 (Step 1 結果) 和 Articut Level 2 結果 (Step 2 結果)

2) 利用 Articut Level 2 結果 將含有動詞的句子取出，並存成 dictionary 的樣子 (請參考 `BuildModel.py` 中的 `getFirstVerbUtterance` function)

   * 此 dictionary 的 key 為第一個動詞的漢語拼音，value 為 含有第一個動詞漢語拼音的句子。
   * 範例如下：

```python

   resDICT = { 'an4': ['按裁判確定前犯數罪者'],
               'bying4fa2': ['數罪併罰', '又數罪併罰'],
               'cai2dying4': ['本院裁定如下',
                              '裁定如主文所示之應執行刑',
                              '裁定如主文',
                              '應於裁定送達後5日內向本院提出抗告狀']
  }   
           
```

3) 自動加入句子到 Loki 。Intent 是上一步驟中 dictionary 的 key ，句子 (utterance) 是上一步驟中 dictionary 的 value。

   * 可參考範例程式檔案 `BuildModel.py` 中的 `addUtterance` function，此 function 利用了新增意圖功能和新增大量句子功能)
   * 此步驟使用的新增意圖功能還有新增大量句子功能可參考 [Loki Tool 文件] (https://github.com/Droidtown/LokiTool_Doc/blob/main/LokiCall/Func_Insert_Utterance.md)
   * 在新增大量句子功能中，請將 `check_list` 內寫入所有 Articut 名詞標記，此步驟是為了要所有輸入至 Loki 模型中的句子名詞都打勾。 請參考 `BuildModel.py` 中的 `InsertUtterance` function

5) 檢查 `tryAgain/firstRound` 的資料夾，如果裡面有東西，就代表有句子可能因為網路原因，沒有被加入。這時，請啟用 `addUtteranceTryAgain.py`。並利用此程式把剩下沒有加入的句子都一起自動加入。

4) 請至 Loki 網站下載所有 project 的 python 檔案

Step 5: 計算相似度的積分

  * 請參考 `StateEvaluation.py`
  * 此檔案中的 `stateEvaluation` 是可以將 `project/intent` 資料夾中的所有 py 檔案中的 `#pass your code here` 都改成 `resultDICT[PROJCET_NAME].append(len([a for a in args if a != ""]))`; 另外 `pass` 改為 `""`
  * 此檔案中的 `changeLokiResultOutput` 是可以將檔案中的主程式 (e.g., `PROJECT_NAME.py`) 的檔案中的 `lokiResultDICT = {}` 改為 `lokiResultDICT = {"PROJCET_NAME":[]}`
  * 此步驟是希望可以計算每一對中句子的 args 數量，args 是句子中有框框的部分。


## 比對模型程式
**說明**

寫一支 python 程式 (e.g., `JudgeSearch.py`) 來執行所有 project 中的 `execLoki`，以便取得所有對中句型的分數。取得分數後就可以算總分

### 一篇裁判書比對一個 Project 為例

1) import 裁判書 project (e.g., `xying2shi4pan4juue2_99_su4_2.py`) 中的 `execLoki` 到 `JudgeSearch.py` 中  

2) 將新的一篇裁判書先以 Articut lv2 斷詞後，取得斷詞結果

3) 使用步驟二中斷詞結果的 `result_pos` ，取出 `result_pos`有動詞的句子，並將這些句子存在 list 中。範例程式請參考 `JudgeSearch.py` 中的 `text2LIST` function

4) 將這些句子放入 execLoki 之中執行，取得結果。結果範例如下：

```python
{'xying2shi4pan4juue2_99_su4_2': [2, 0, 0, 1, 2, 3, 1, 0, 2, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 0, 2, 0, 0, 5, 3]}
```

5) 加總分數，此積分即為新裁判書和此模型 (e.g., `刑事判決_99,訴,2`) 的相似程度。分數越高，代表此新裁判書和這個模型越像。

### 一篇裁判書比對多個 Project
可使用平行運算來讓同一篇新裁判書可以比對數個 project。程式範例請見 `JudgeSearch.py`

