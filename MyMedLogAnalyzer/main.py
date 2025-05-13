import xml.etree.ElementTree as ET
import json
import re
import pathlib
import os
import dic_fo_did_bsid
import datetime

_main_path = ""

_logDictionary = {}
_dicSessionIdUserId = {}
_dicResults = {}

# 正規表現
_reg_sessionID_userID = re.compile(r'\[[0-9a-zA-Z]+\t[0-9a-zA-Z]+\]')
_reg_sessionID = re.compile(r'(?<=\[)[0-9a-zA-Z]+(?=\t)')
_reg_userID = re.compile(r'(?<=\t)[0-9a-zA-Z]+(?=\])')

# 定義
MDOFFICELOG_SAVED_PATH = r"C:\temp\MdOffice_logs"
MDMY_SAVED_PATH = r"C:\temp\MdMy_logs"
OUTPUT_CSV = r"c:\temp\MdOffice_log_analysis4.csv"

# 無視リスト
_ignore_uid = [
"d8846c86e7324463a043e3ddffdddab1",
"4610f89d0dd144f0898edd5318a16f46",
"d5833e3c998b4657acca7487284273b2",
"7c2ba107bbf04863967a9e9304f3ae36",
"31859f4cf3b54f15bec26d4d0b364c61",
"df36bba71a53465c94ca93651d96e4b1",
"899989bc617140929dbc3631f7424169"
"7867b70f806a403a971a3b66396c4f9b"
]
# 6 確認用
# 424 島津メディカルシステムズ株式会社 技術本部 技術センター
_ignore_fno = [-1, 3, 6, 424]
_ignore_did = [-1, 1, 674, 684, 4, 173, 6, 5, 83, 536, 516, 482, 67, 414, 440, 579, 424, 418, 551, 491, 578, 66, 468, 183, 460, 433, 545, 132, 265, 499, 500, 501, 498, 586, 145, 402, 80, 426, 601, 598, 596, 597, 600, 258, 48, 178, ]
#_ignore_fnoにリストした施設の装置のBS_IDが列挙されていること
_ignore_bsid = [
-1,
194103,
189884,
189257,
189892,
189896,
192631
]

_start_date = datetime.datetime.strptime("2023/4/1", "%Y/%m/%d")
_end_date = datetime.datetime.strptime("2050/1/1", "%Y/%m/%d") #含まない

def getMdxxlogFileList(pt, ext):
    path = pathlib.Path(pt)
    files = path.glob(ext)
    return files

"""
削除予定
def getMdOfficelogFileList():
    path = pathlib.Path(MDOFFICELOG_SAVED_PATH)
    files = path.glob("**/*.log")
    return files
"""

def getSessionIdAndUserId(line):
    return getSessionId(line), getUserId(line)
    
def getSessionId(line):
    try:
        result = _reg_sessionID.search(line)
        if result:
            return result.group(0)
    except:
        return

def getUserId(line):
    try:
        result = _reg_userID.search(line)
        if result:
            return result.group(0)
    except:
        return

def printA():
    for userId, v in _logDictionary.items():
        for sessionId, v0 in v.items():
            for l in v0:
                print(f"{sessionId}, {userId} -> {l}", end='')
    return

def printCsv(csv_all, isHeader):
    if isHeader == True:
        fw = open(OUTPUT_CSV, "w")
        print("datetime,UserId,SessionId,tagname,facility No,device id,BS_ID,base search", file=fw)
    else:
        fw = open(OUTPUT_CSV, "a")

    for csv in csv_all:
        print(f"{csv[0]},{csv[1]},{csv[2]},{csv[3]},{csv[4]},{csv[5]},{csv[6]},{csv[7]}", file=fw)
    fw.close()

def printResults():
    fw = open(OUTPUT_CSV, "w")
    print("datetime,UserId,SessionId,tagname,facility No,device id,BS_ID,base search", file=fw)
    
    for k in _dicResults:
        ll = _dicResults[k]
        for csv in ll:
            print(f"{csv[0]},{csv[1]},{csv[2]},{csv[3]},{csv[4]},{csv[5]},{csv[6]},{csv[7]}", file=fw)
    fw.close()

def IsIgnoreUid(id):
    for uid in _ignore_uid:
        if uid == id:
            return True
    return False

def IsIgnore(list, value):
    for v in list:
        if v == value:
            return True
    return False

def chedkDuplication(list, addcsv, item_num):
    # 最初はlistは空
    if len(list) == 0:
        return False

    check_line = ""
    for ww in addcsv:
        check_line = check_line + "," + str(ww)

    for csv in list:
        line = ""
        for ww in csv:
            line = line + "," + str(ww)
        
        if line == check_line:
            return True

    return False

# session id
#
# datetime,UserId, SessionId, tagname, facility No, device id, base search
#
def analysis(searchword, reg_getvalue, tagname, action):
    global _dicResults
    rrr = re.compile(searchword)
    rr = re.compile(reg_getvalue)
    csv_all = []
    for sessionId, v0 in _logDictionary.items():
        find_searchword = False
        for line in v0:
            if find_searchword:
                # searchwordが見つかっているのでregを探索する
                rr_result = rr.search(line)
                if rr_result:
                    facilityno, deviceid, bsid = action(rr_result.group(0))
                    #print(f"facilityno = {facilityno}")
                    uid = _dicSessionIdUserId[sessionId]
                    if IsIgnore(_ignore_uid, _dicSessionIdUserId[sessionId]) == False and IsIgnore(_ignore_fno, facilityno) == False and IsIgnore(_ignore_did, deviceid) == False and IsIgnore(_ignore_bsid, bsid) == False:
                        #print(f"find!!! {reg_getvalue} -> {rr_result.group(0)} -> {v}")
                        csv = [
                            getTimesamp(line),
                            _dicSessionIdUserId[sessionId],
                            sessionId,
                            tagname,
                            facilityno,
                            deviceid,
                            bsid,
                            searchword
                        ]
                        # 重複のチェック
                        if chedkDuplication(csv_all, csv, 8):
                            # 重複あり、何もしない
                            pass
                        else:
                            csv_all.append(csv)

                        #
                        try:
                            _dicResults[facilityno].append(csv)
                        except:
                            _dicResults.setdefault(facilityno, [csv])

                        # 戻す
                        find_searchword = False
                        
            else:
                # searchwordを見つける
                result = rrr.search(line)
                if result:
                    #print("find!!!")
                    find_searchword = True
    return csv_all


# ファイルを一つずつ処理する
def readMdOfficeLog(file_name):
    global _logDictionary
    global _dicSessionIdUserId
    
     #ファイル読込
    with open(file_name, encoding="utf-8") as f:
        i = 0
        for line in f:
            i = i + 1
            #print(line)
            
            #範囲チェック 2023/04/01 00:00:49
            try:
                isPeriodOk = False
                buf_timestamp = getTimesamp(line)
                timestamp = datetime.datetime.strptime(buf_timestamp, "%Y/%m/%d %H:%M:%S")
                if _start_date <= timestamp:
                    if timestamp < _end_date:
                        isPeriodOk = True
                
                if isPeriodOk == False:
                    continue
            except:
                continue

            try:
                result = _reg_sessionID_userID.search(line)
                if result:
                     # session idとuser idを取り出してをペアで保存する
                    sessionId, userId = getSessionIdAndUserId(line)
                    if sessionId != "" and userId != "" and userId != "null" and (sessionId not in _dicSessionIdUserId):
                        _dicSessionIdUserId.setdefault(sessionId, userId)
                        
                    if sessionId != "": # session idだけに注目
                        try:
                            _logDictionary[sessionId].append(line)
                        except:
                            _logDictionary.setdefault(sessionId, [line])
            except:
                return False
    return True

def actionDeleteLeftArc(s):
    return s.replace('(', '')

# 2023/04/01 00:10:35.927	INFO...
def getTimesamp(s):
    return s[0:19]

# ユーザ登録時
def actionUserRegistration(s):
    try:
        s = s.replace('(', '').replace("'", "").replace(' ', '')
        return int(s), 0, 0
    except:
        return -1, -1, -1


# 装置登録時
def actionGetFacilityNoWhenRegistDevice(s):
    try:
        s = s.replace('(', '').replace("'", "").replace(' ', '')
        sl = s.split(',')
        fno = sl[1]
        did = sl[0]
        if did.isdecimal() and fno.isdecimal():
            #print(f"{s} -> {sl[1]}")
            return int(fno), int(did), 0
    except:
        return -1, -1, -1
    return -1, -1, -1

# 施設詳細画面表示の拡張処理
def actionOpenFacilityDetailPage(s):
    try:
        return int(s), 0, 0
    except:
        return -1, -1, -1

# 装置詳細画面の表示の拡張処理
def actionOpenModarityDetailPage(s):
    try:
        did = int(s)
        fno, bsid = dic_fo_did_bsid.get_fno_bsid(did)
        return fno, did, bsid
    except:
        return -1, -1, -1
    
# アラート詳細画面の表示の拡張処理
def actionOpenAlartPage(s):
    try:
        did = int(s)
        fno, bsid = dic_fo_did_bsid.get_fno_bsid(did)
        return fno, did, bsid
    except:
        return -1, -1, -1

# 確認コメントの登録の拡張処理
def actionRegistConfirm(s):
    try:
        return int(s), 0, 0
    except:
        return -1, -1, -1
    
# 撮影詳細画面の表示の拡張処理
def actionOperationPage(s):
    try:
        bsid = int(s)
        fno, did = dic_fo_did_bsid.get_fno_did(bsid)
        return fno, did, bsid
    except:
        return -1, -1, -1

# 解消されましたかボタンクリックの拡張処理
def actionCustemerConfirmClick(s):
    try:
        did = int(s)
        fno, bsid = dic_fo_did_bsid.get_fno_bsid(did)
        return fno, did, bsid
    except:
        return -1, -1, -1

# サービスレポート表示の拡張処理
def actionServiceReportDownload(s):
    try:
        bsid = int(s)
        fno, did = dic_fo_did_bsid.get_fno_did(bsid)
        return fno, did, bsid
    except:
        return -1, -1, -1

def main():
    global OUTPUT_CSV

    print("MdOfficeログの解析を実行します")

    OUTPUT_CSV = rf"{_main_path}\MdOffice_log_analysis.csv"

    # MdOfficeログファイルのリストを取得
    files = getMdxxlogFileList(MDOFFICELOG_SAVED_PATH, "**/*.log")
    
    """"""
    for file in files:
        readMdOfficeLog(file)
    
    # 施設詳細画面表示
    """"""
    csv_all = analysis(
        "GetFacilityInfoLogic\texecMainLogic start",
        "(?<=WHERE facility_no \= ).+(?= ORDER BY)", 
        "施設詳細画面表示", 
        actionOpenFacilityDetailPage)
    #printCsv(csv_all, False)

    # 装置の登録
    """"""
    csv_all = analysis(
        "insertDeviceIsid\(\) start", 
        "(?<=VALUES).+(?=,)", 
        "装置登録", 
        actionGetFacilityNoWhenRegistDevice)
    #printCsv(csv_all, True)

    # 装置詳細画面の表示
    """"""
    csv_all = analysis(
        "ServiceServicereportListLogic\texecMainLogic\(\) start", 
        "(?<=WHERE facility_no \= ).+(?= ORDER BY)", 
        "装置詳細画面表示", 
        actionOpenModarityDetailPage)
    #printCsv(csv_all, False)

    # アラート詳細画面の表示
    """"""
    csv_all = analysis(
        "GetAlertDetailLogic\texecMainLogic\(\) start", 
        "(?<=WHERE isid\.device_isid_no \= ).+$", 
        "アラート詳細画面表示", 
        actionOpenAlartPage)
    #printCsv(csv_all, False)

    # 確認コメントの登録
    """"""
    csv_all = analysis(
        "AddSupportHistoryLogic\texecMainLogic\(\) start", 
        "(?<=And di\.device_isid_no \= ).+(?= \t AND)", 
        "確認コメント登録", 
        actionOpenAlartPage)
    #printCsv(csv_all, False)

    # 撮影詳細画面の表示
    #"(?<={""type"":""BS_ID"",""value"":"").+(?=""}" + "} response)", 
    csv_all = analysis(
        "DeviceOperationLogic\texecMainLogic\(\) start", 
        '(?<={"type":"BS_ID","value":").+(?="}} response)', 
        "撮影詳細画面表示", 
        actionOperationPage)
    #printCsv(csv_all, False)

    printResults()

    print("---終了----")
    return 0

def main2():
    global OUTPUT_CSV

    print("MdMyログの解析を実行します")

    OUTPUT_CSV = rf"{_main_path}\MdMy_log_analysis.csv"

    # MdMyログファイルのリストを取得
    files = getMdxxlogFileList(MDMY_SAVED_PATH, "**/*.log")

    for file in files:
        readMdOfficeLog(file)
    
    # 施設詳細画面表示
    """"""
    csv_all = analysis(
        "GetFacilityDevicesLogic\tgetFacilityDevices start",
        "(?<=WHERE tf.facility_no = ').+(?=' AND)", 
        "施設詳細画面表示", 
        actionOpenFacilityDetailPage)
    
    # 装置詳細画面の表示
    """"""
    csv_all = analysis(
        "CustomerServicereportListLogic\texecMainLogic\(\) start", 
        "(?<= and isid\.device_isid_no \= ).+$", 
        "装置詳細画面表示", 
        actionOpenModarityDetailPage)
    
    # アラート詳細画面の表示
    """"""
    csv_all = analysis(
        "CustomerGetAlertDetailLogic\texecMainLogic\(\) start", 
        "(?<= and isid\.device_isid_no \= ).+$", 
        "アラート詳細画面表示", 
        actionOpenAlartPage)
    
    # 解消されましたかボタンのクリック
    """"""
    csv_all = analysis(
        "AddSupportHistoryLogic\texecMainLogic\(\) start", 
        "(?<= and isid\.device_isid_no \= ).+$", 
        "解消されましたか送信", 
        actionCustemerConfirmClick)
    
    # サービスレポート表示
    """"""
    csv_all = analysis(
        "ServicereportFileLogic\tmakePath\(\) start", 
        "(?<=/BS_ID/)\d+(?=/)", 
        "サービスレポート表示", 
        actionServiceReportDownload)
    
    printResults()

    print("---終了----")

def main_test():
    print("テストです！！！")

    # MdMyログファイルのリストを取得
    files = getMdxxlogFileList(MDMY_SAVED_PATH, "**/*.log")

    for file in files:
        readMdOfficeLog(file)
    
    # ユーザ登録
    """"""
    csv_all = analysis(
        "UserRegisterLogic\tUserRegisterLogic execMainLogic\(\) start",
        "(?<=WHERE tf.facility_no = ').+(?=' AND)", 
        "ユーザ登録", 
        actionUserRegistration)
    
if __name__=='__main__':

    # 実行フォルダ（main.pyがあるフォルダ）
    _main_path = os.path.dirname(os.path.abspath(__file__))

    #main()
    main2()
    #main_test()