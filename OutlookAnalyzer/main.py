import win32com.client
import csv
import os
import re
import pytz
from datetime import datetime


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

_target_folder = ["医用","サ統","ThingWorx","TWアラート","ConnectionStatusDetection","SMS"]

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
Customer: Good Heart Foundation\r\n
Room: CATH LAB\r\n
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
    
    return customer, room, model, axedasn, date, state

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
        if item.Class == 43:  # 43はメールアイテムのクラス
            customer, room, model, axedasn, date, state = getBody(item.Body)
            #print(f"{item.Subject},{item.SentOn},{item.ReceivedTime},\"{item.Body}\"", file=fw)
            subject = item.Subject
            japan_time = getJapanTZ(date)
            #print(f"item.SentOn={item.SentOn}")
            senton = str(item.SentOn).replace("+00:00", "") #謎、日本時間なのに+00:00と標準時間のような表現になっている
            #print(f"senton={senton}")
            receivedtime = str(item.ReceivedTime).replace("+00:00", "") #謎、日本時間なのに+00:00と標準時間のような表現になっている
            #subject = subject.encode("shift-jis").decode("utf-8", errors="ignore")
            print(f"\"{subject}\",\"{senton}\",\"{receivedtime}\",\"{customer}\",\"{room}\",\"{model}\",\"{axedasn}\",\"{date}\",\"{state}\",\"{japan_time}\"", file=fw)
    fw.close()

    print('メール情報をoutput.csvにエクスポートしました。')

if __name__=='__main__':

    # 実行フォルダ（main.pyがあるフォルダ）
    _main_path = os.path.dirname(os.path.abspath(__file__))

    main()
