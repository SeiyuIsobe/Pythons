import win32com.client
import csv
import os
import re
import pytz
from datetime import datetime
from models import DR_300
from models import FLUOROspeed_X1
from models import BresTome
from models import CVS_MPC
from models import CVS_MPC_2
from models import DAR_3500
from models import DAR_7500
from models import DAR_8000
from models import DR_200
from models import Elmammo
from models import FlexaF3
from models import FlexaF4
from models import PET_MPC
from models import RADspeedProEDGE
from models import Trinias
from models import Trinias_Opera
from models import Trinias_smart


"""
# PSTファイルの読み込み
pst_file_path = r"C:\temp\ConnectionStatusDetection_export.pst"
outlook.AddStore(pst_file_path)

# CSVファイルの作成
with open('output.csv', mode='w', encoding='utf-8', newline='') as csv_file:
    fieldnames = ['Subject', 'SentOn', 'ReceivedTime', 'Body']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

    # メールの取得とCSVへの書き出し
    for item in items:
        if item.Class == 43:  # 43はメールアイテムのクラス
            writer.writerow({
                'Subject': item.Subject,
                'SentOn': item.SentOn,
                'ReceivedTime': item.ReceivedTime,
                'Body': item.Body
            })
"""

_reg_Customer = re.compile(r'(?<=Customer: )+.+(?=\r\n)')
_reg_Room = re.compile(r'(?<=Room: )+.+(?=\r\n)')
_reg_Model = re.compile(r'(?<=Model: )+.+(?=\r\n)')
_reg_AxedaSN = re.compile(r'(?<=Axeda S/N: )+.+(?=\r\n)')
_reg_Date = re.compile(r'(?<=Date: )+.+(?=\r\n)')
_reg_State = re.compile(r'(?<=State: )+.+(?=\r\n)')

_target_folder = ["医用","サ統","ThingWorx","TWアラート"]

_assetDic = {}

#=====================
#---------------------
#      入力パラメータ
#
#検索
_doSearch = True
#
#検索文字列
_search_string = "**" #SMS
#_search_string = "" #検索Wordなし→全検索
#
#対象の期間は？　指定する=True、指定しない=False
IS_PERIOD = True
#
#IS_PERIOD = Trueの場合
#開始日時
START_PERIOD_DATE = "2025/5/1 00:00:00"
#終了日時
END_PERIOD_DATE = "2025/5/31 23:59:59"
#---------------------
#=====================

# 期間指定
_isPeriod = IS_PERIOD
_fromPeriod = datetime.strptime(START_PERIOD_DATE, "%Y/%m/%d %H:%M:%S")
_toPeriod = datetime.strptime(END_PERIOD_DATE, "%Y/%m/%d %H:%M:%S")
_dic_month = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}

"""
TW ConnectionStatusDetection : Good Heart Foundation CATH LAB
"""
def getSubject(subject_str):
    customer = ""
    r = _reg_Customer.search(subject_str)
    if r:
        customer = r.group()
    return customer

"""
Bodyの中身
Customer: **MMS** St. Tammany Parish SVG4\r\n
Room: SMS20190049: SVG4\r\n
Model: Trinias.smart\r\n
Axeda S/N: SN2E9155D23000\r\n
Date: 2025-01-24 13:08:31.837 UTC+05:30\r\n
State: false\r\n
"""
def getBody(body_str):
    customer = ""
    room = ""
    model = ""
    axedasn = ""
    date = ""
    state = ""
    
    r = _reg_Customer.search(body_str)
    if r:
        customer = r.group()

    r = _reg_Room.search(body_str)
    if r:
        room = r.group()

    r = _reg_Model.search(body_str)
    if r:
        model = r.group()

    r = _reg_AxedaSN.search(body_str)
    if r:
        axedasn = r.group()

    r = _reg_Date.search(body_str)
    if r:
        date = r.group()

    r = _reg_State.search(body_str)
    if r:
        state = r.group()
    
    #[Error]以降に記載されているアラートを取得
    lines = re.split('\r\n', body_str)
    isError = False
    errors = []
    for line in lines:
        if line == "[Error]":
            isError = True
            continue
        if isError:
            #改行のみは終端
            if line == "":
                break
            #アラートを取得
            errors.append(line)

    return customer, room, model, axedasn, date, state, errors

#
# utc_str: 2025-01-24 13:08:31.837 UTC+05:30
#
def getJapanTZ(utc_str):

    #チェック
    if("UTC +00:00" in utc_str):
        # 文字列をdatetimeオブジェクトに変換
        utc_time = datetime.strptime(utc_str, "%Y-%m-%d %H:%M:%S.%f UTC %z")
    else:
        if("." in utc_str):
            if("UTC" in utc_str):
                # 文字列をdatetimeオブジェクトに変換
                utc_time = datetime.strptime(utc_str, "%Y-%m-%d %H:%M:%S.%f UTC%z")
            else:
                # 文字列をdatetimeオブジェクトに変換
                utc_time = datetime.strptime(utc_str, "%Y-%m-%d %H:%M:%S.%f%z")
        else:
            # 文字列をdatetimeオブジェクトに変換
            utc_time = datetime.strptime(utc_str, "%Y-%m-%d %H:%M:%S%z")

    try:
        # 日本時間のタイムゾーンを取得
        japan_tz = pytz.timezone('Asia/Tokyo')

        # UTC時間を日本時間に変換
        japan_time = utc_time.astimezone(japan_tz)

        # 結果を表示
        #print("日本時間:", japan_time.strftime("%Y-%m-%d %H:%M:%S.%f"))

        return japan_time.strftime("%Y-%m-%d %H:%M:%S.%f")

    except:
        print(f"getJapanTZ error. utc_str = {utc_str}")

#date_line
#2025-05-31 03:02:08.558
def isPeriod(date_line):
    #期間指定なし
    if(_isPeriod == False):
        return True
    
    #日付型に変換
    obj_date = getDateObject(date_line)
    
    if(_fromPeriod <= obj_date <= _toPeriod):
        return True
    
    return False

# 対応書式：2025-05-31 03:02:08.558
def getDateObject(line):
    try:
        d0 = re.split('[-/: .]', line)
        return datetime(
            int(d0[0]),
            int(d0[1]),
            int(d0[2]),
            int(d0[3]),
            int(d0[4]),
            int(d0[5])
            )
    except Exception as e:
        print(f"except!!! {e} -> {line}")

    return datetime(1900, 1, 1, 0, 0, 0, 0)

def createModel(model):
    if model == "DR-300":
        obj_model = DR_300()
    elif model == "FLUOROspeed.X1":
        obj_model = FLUOROspeed_X1()
    elif model == "BresTome":
        obj_model = BresTome()
    elif model == "CVS_MPC":
        obj_model = CVS_MPC()
    elif model == "CVS_MPC_2":
        obj_model = CVS_MPC_2()
    elif model == "DAR-3500":
        obj_model = DAR_3500()
    elif model == "DAR-7500":
        obj_model = DAR_7500()
    elif model == "DAR-8000":
        obj_model = DAR_8000()
    elif model == "DR-200":
        obj_model = DR_200()
    elif model == "Elmammo":
        obj_model = Elmammo()
    elif model == "FlexaF3":
        obj_model = FlexaF3()
    elif model == "FlexaF4":
        obj_model = FlexaF4()
    elif model == "PET_MPC":
        obj_model = PET_MPC()
    elif model == "RADspeedProEDGE":
        obj_model = RADspeedProEDGE()
    elif model == "Trinias":
        obj_model = Trinias()
    elif model == "Trinias.Opera":
        obj_model = Trinias_Opera()
    elif model == "Trinias.smart":
        obj_model = Trinias_smart()
    
    return obj_model

def main():
    # Outlookアプリケーションの接続
    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")

    # PSTファイルの読み込み -> 現在未使用、受信フォルダを対象とする場合は不要
    if(False):
        pst_file_path = r"C:\temp\ConnectionStatusDetection_export.pst"
        outlook.AddStore(pst_file_path)

    # ルートフォルダの取得
    root_folder = outlook.Folders["s-isobe@shimadzu.co.jp"]

    # 目的のフォルダの取得
    #folder = root_folder.Folders["医用"].Folders["サ統"].Folders["ThingWorx"].Folders["TWアラート"].Folders["ConnectionStatusDetection"]
    for target_folder in _target_folder:
        root_folder = root_folder.Folders[target_folder]
    folder = root_folder

    # メールを取得
    items = folder.Items

    fw = open("output.csv", "w", encoding="utf-8")
    print("Subject,SentOn,ReceivedTime,Customer,Room,Model,Axeda S/N,Date,State,Date_JST", file=fw)
    # メールの取得とCSVへの書き出し
    for item in items:

        #件名の検索
        if len(_search_string) == 0: #検索しない場合はpass
            pass
        elif _search_string in item.Subject: #件名が一致する場合はpass
            pass
        else:
            continue

        if item.Class == 43:  # 43はメールアイテムのクラス
            #メールの内容を取得
            customer, room, model, axedasn, date, state, errors = getBody(item.Body)
            
            #メールの内容をCSV出力する内容に変換
            subject = item.Subject
            japan_time = getJapanTZ(date)
            senton = str(item.SentOn).replace("+00:00", "") #謎、日本時間なのに+00:00と標準時間のような表現になっている
            receivedtime = str(item.ReceivedTime).replace("+00:00", "") #謎、日本時間なのに+00:00と標準時間のような表現になっている
            
            #期間範囲
            if isPeriod(japan_time):
                pass
            else:
                continue

            #モデルオブジェクト生成
            obj_model = createModel(model)

            #モデルオブジェクトの保持
            if axedasn in _assetDic.keys():
                obj_model = _assetDic[axedasn]
            else:
                _assetDic.setdefault(axedasn, obj_model)

            #アラート登録
            for error in errors:
                #アラートを登録
                obj_model.registerAlert(error, japan_time)

            #出力
            print(f"\"{subject}\",\"{senton}\",\"{receivedtime}\",\"{customer}\",\"{room}\",\"{model}\",\"{axedasn}\",\"{date}\",\"{state}\",\"{japan_time}\"", file=fw)
    fw.close()
    print('メール情報をoutput.csvにエクスポートしました。')

    # アラート情報の出力
    fw = open("output_alert.csv", "w", encoding="utf-8")
    print("Axeda S/N,Model,Alert Name,Alert Dates(JST)", file=fw)
    for key_axedasn, value_model in _assetDic.items():
        for alert_name, alert_dates_list in value_model.Alertdic.items():
            for alert_date in alert_dates_list:
                print(f"\"{key_axedasn}\",\"{value_model.Name}\",\"{alert_name}\",\"{alert_date}\"", file=fw)
    fw.close()
    print('アラート情報をoutput_alert.csvにエクスポートしました。')

if __name__=='__main__':

    # 実行フォルダ（main.pyがあるフォルダ）
    _main_path = os.path.dirname(os.path.abspath(__file__))

    main()
