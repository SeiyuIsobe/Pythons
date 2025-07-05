import os
import re
import pandas as pd
from geopy.geocoders import Nominatim
from haversine import haversine
import time
import csv
from geopy.distance import geodesic
from datetime import date
import focal_map

#begin---------入力パラメータ----------------------------------
#震源地リストファイル
g_focallist_file = r"in\focallist.txt"
#納入リストファイル
g_devicelist_file = r"in\納入システム_10_utf-8.csv"
#観測点リストファイル
g_sonarlist_file = r"sonarpointlist.csv"
#DB
g_DB_devicelist_file = r"DB\db.csv"
#結果
g_devicechecklist_file = r"out\check_devices_list_sjis.csv"
g_focallist_csv_file = r"out\focallist.csv"
#end---------入力パラメータ------------------------------------

# ジオロケーターの初期化
geolocator = Nominatim(user_agent="myGeocoder")

#ログ
g_logs = []

#読込カウンター
g_loadcounter = 0

def loading(init=False):
    global g_loadcounter

    if init:
        g_loadcounter = 0
        print(f"\r-----", end="")
        return

    if g_loadcounter == 0:
        print(f"\rO----", end="")
    elif g_loadcounter == 1:
        print(f"\roO---", end="")
    elif g_loadcounter == 2:
        print(f"\r.oO--", end="")
    elif g_loadcounter == 3:
        print(f"\r-.oO-", end="")
    elif g_loadcounter == 4:
        print(f"\r--.oO", end="")
    elif g_loadcounter == 5:
        print(f"\r---.o", end="")
    elif g_loadcounter == 6:
        print(f"\r----.", end="")
    elif g_loadcounter == 7:
        print(f"\r-----", end="")
    elif g_loadcounter == 8:
        print(f"\r----O", end="")
    elif g_loadcounter == 9:
        print(f"\r---Oo", end="")
    elif g_loadcounter == 10:
        print(f"\r--Oo.", end="")
    elif g_loadcounter == 11:
        print(f"\r-Oo.-", end="")
    elif g_loadcounter == 12:
        print(f"\rOo.--", end="")
    elif g_loadcounter == 13:
        print(f"\ro.---", end="")
    elif g_loadcounter == 14:
        print(f"\r.----", end="")
    elif g_loadcounter == 15:
        print(f"\r-----", end="")
        g_loadcounter = 0
        return

    g_loadcounter = g_loadcounter + 1
    return



def writeLog(typestring, detail):
    dt = "{0:%Y/%m/%d %H:%M:%S}".format(date.today())
    with open("error_log.txt", "+a", encoding="utf-8") as f:
        print(f"{dt} {typestring} {detail}", file=f)

def to_float(s):
    try:
        return float(s)
    except:
        return None

"""
CSVのフォーマットは以下
・一行目：項目名
・二行目以降：データ
地域名称,震度観測点名称,観測点所在地,緯度(度),緯度(分),経度(度),経度(分),観測開始(yyyymmddhhmm),観測終了(yyyymmddhhmm),緯度,経度,Google Map
新潟県上越,糸魚川市一の宮,糸魚川市一の宮1-2-5（糸魚川市役所）,37,2.3,137,51.8,1.99604E+11,,37.03833333,137.8633333,"https://www.google.com/maps?q=37.0383333333333,137.863333333333"
・・・
"""
def loadSonarPointList():
    with open(g_sonarlist_file, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        data = []
        for row in reader:
            # 必要に応じて数値に変換
            row["緯度(度)"] = to_float(row["緯度(度)"])
            row["緯度(分)"] = to_float(row["緯度(分)"])
            row["経度(度)"] = to_float(row["経度(度)"])
            row["経度(分)"] = to_float(row["経度(分)"])
            row["緯度"]    = to_float(row["緯度"])
            row["経度"]    = to_float(row["経度"])
            data.append(row)
    return data

"""
度分秒（例: 42°21.3'N）を10進数（float）に変換
"""
def dms_to_decimal(dms_str):
    try:
        match = re.match(r"(\d+)°\s*(\d+(?:\.\d+)?)'([NSEW])", dms_str.strip())
        if not match:
            raise ValueError(f"Invalid DMS format: {dms_str}")
        degrees = int(match.group(1))
        minutes = float(match.group(2))
        direction = match.group(3)
        decimal = degrees + minutes / 60
        if direction in ['S', 'W']:
            decimal *= -1
        return decimal
    except:
        return None

# 郵便番号をハイフン付きに変換する関数
def format_postal_code(postal_code):
    try:
        if len(postal_code) == 7 and postal_code.isdigit():
            return f"{postal_code[:3]}-{postal_code[3:]}"
        return postal_code
    except:
        writeLog("ERROR", f"郵便番号の形式が不正なので緯度・軽度の取得に失敗しました：{postal_code}")
        return None

# 郵便番号の緯度・経度を取得する関数（リトライ機能付き）
def get_location(postal_code, retries=10):
    for attempt in range(retries):
        try:
            #郵便番号のフォーマット修正
            postal_code = format_postal_code(postal_code)
            if postal_code == None:
                return None, None
            
            ret = geolocator.geocode(postal_code, timeout=10)  # タイムアウトを10秒に設定
            return ret, postal_code
        except Exception as e:
            print(f"{postal_code} : エラーが発生しました: {e}. リトライ中... ({attempt + 1}/{retries})")
            time.sleep(2)  # リトライ間隔を2秒に設定
    
    return None, None

"""
震源地リストを読込んでCSVに書き出す
　震源地リストは気象庁HP→各種データ・資料→震源地リスト
　震源リスト（クリックして開閉する）、目的の日のリストをコピペ
　フォーマットは以下の通り（2025/6月現在）
　　1行目：ヘッダ
　　2行目以降：データ
　　　　データは空白区切り
　　　　「-」が連続する区切り行あり
　　　　空白の行あり
0    1  2  3  4  5     6         7          8        9   10
年   月 日 時 分 秒    緯度       経度       深さ(km)  Ｍ   震央地名
-----------------------------------------------------------------------------------------
2025  6 13 00:00  8.0  42°21.3'N 144°33.4'E   20     2.2  釧路沖                     
2025  6 13 00:01 39.7  34°36.9'N 136° 5.7'E   54     0.2  三重県中部                   
・・・

"""
def loadFocalPointList():
    print(f"震源地リストを読込みます：{g_focallist_file}")

    loading(True)

    rows = []
    with open(g_focallist_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip()
            # 「-」だけの行は無視
            if re.match(r'^-+$', line):
                continue
            # 空行は無視
            if not line.strip():
                continue
            #°の後に空白がある場合と、無い場合がある
            # 「°」の直後の空白を削除
            line = re.sub(r'°\s+', '°', line)
            # 行を空白で分割（複数空白も区切り）
            fields = re.split(r'[\s:]+', line.strip())
            rows.append(fields)

            loading()

    #CSVファイルに書き込む
    with open(g_focallist_csv_file, 'w', encoding='sjis', newline='') as f:
        writer = csv.writer(f)
        isFirstRow = True
        # 各行を書き込む
        for row in rows:
            # ヘッダーを追加
            if isFirstRow:
                writer.writerow([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], "Latitude", "Longitude"])
                isFirstRow = False
                continue
            if len(row) >= 11:
                # 緯度と経度を度分に変換
                lat_deg = dms_to_decimal(row[6])
                lon_deg = dms_to_decimal(row[7])
                # 書き込む行を作成
                writer.writerow([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], lat_deg, lon_deg])
    
    #CSVファイルを読込む
    with open(g_focallist_csv_file, "r", encoding="sjis", newline="") as f:
        reader = csv.DictReader(f)
        data = []
        for row in reader:
            data.append(row)
    
    print(f"\r...完了")
    return data


"""
例：
CC_ID,BS_ID,郵便番号,緯度,経度,Source
"""
def DBLoadDeviceList():
    #存在チェック
    if os.path.exists(g_DB_devicelist_file) == False:
        print(f"DBを作成します：{g_DB_devicelist_file}")
        with open(g_DB_devicelist_file, "w", encoding="utf-8") as f:
            print("CC_ID,BS_ID,郵便番号,緯度,経度,Source", file=f)
        print("...完了")
        return []

    print(f"DBを読込みます：{g_DB_devicelist_file}")
    with open(g_DB_devicelist_file, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        data = []
        for row in reader:
            data.append(row)
    print("...完了")
    return data

"""
例：
BS_ID,システム種別,システム名,システムSN,使用開始日,廃棄日,-,CC_ID,顧客名,設置室名,納入区分,-,通常デモダミーフラグ,サービス担当店,販売担当店（島津製作所）,販売担当店（島津MS/代理店）,販売担当店（MS卸）,国コード,国,都道府県,住所,顧客TEL,顧客FAX,顧客側担当者様1,顧客様TEL1,顧客側担当者様2,顧客様TEL2,FAX,E-Mail,サービス担当者,診療科・部署,備考,ユニットラベル貼付日,旧BS_ID,-,-,-,装置情報,-,保守,郵便番号
193999,X線(一般),EZy-Rad Pro/X'sy Anesis A,MQC8321E8022,2024/11/5,,,80299,Dsこどもとみんなのクリニック,,新品,,通常,島津MS-東海支店-名古屋第一技術課,島津製作所-営業企画OEM,島津MS-東海支店-営業課(販),,JP,日本,愛知県,愛知県愛知郡東郷町大字春木字桝池39-1,0561-56-6545,,,,,,,,,,,,,,,,有,,なし,470-0162
"""
def LoadDeviceList():
    print(f"納入リストを読込みます：{g_devicelist_file}")
    #存在チェック
    if os.path.exists(g_devicelist_file) == False:
        print(f"ファイルが見つかりません：{g_devicelist_file}")
        exit()

    #リストの内容をまずは全て読込む
    try:
        with open(g_devicelist_file, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            data = []
            for row in reader:
                data.append(row)
        print("...完了")
        return data
    except:
        print(f"納入リストの読み込みエラー！！！：{g_devicelist_file}")
        print(f"UTF-8で保存し直してもう一度実行してください")
        exit()
    print("...完了")
    return data

#進捗表示
def showProgress(mess, curr, total, bar_length):

    step = int(100/bar_length)
    curr_progress = int(curr/total*100)
    bar = ""
    for i in range(bar_length): #i = 0, ..., bar_length-1
        if (i+1)*step <= curr_progress:
            bar = f"{bar}*"
        else:
            bar = f"{bar}-"

    # 進捗表示
    print(f"\r{mess}[{bar}] {curr_progress}%", end="")
        
        

"""->

<-"""
def searchTable(target_table, target_item_name1, target_item1, target_item_name2, target_item2):
    for row in target_table:
        if target_item1 == row[target_item_name1] and target_item2 == row[target_item_name2]:
            return row
    return None

def UpdateDB(db, devices):
    print("DBを更新します：", end="")
    num_db = len(db)
    num_devices = len(devices)

    updaete_db = []
    #db -> new_dbを作る
    #db -> update_dbにコピー
    i_row = -1
    for row in db:
        i_row +=1

        #進捗表示
        showProgress("DBを更新します：", i_row + 1, num_db + num_devices, 20)

        new_row = {}

        #納入リストに合致するレコードがないか確認
        d = searchTable(devices, "CC_ID", row['CC_ID'], "BS_ID", row['BS_ID'])

        #納入リストに無い　→　そのままコピー
        if d == None:
            new_row.setdefault("CC_ID", row["CC_ID"])
            new_row.setdefault("BS_ID", row["BS_ID"])
            new_row.setdefault("郵便番号", row["郵便番号"])
            new_row.setdefault("緯度", row["緯度"])
            new_row.setdefault("経度", row["経度"])
            new_row.setdefault("Source", row["Source"])
        
        #納入リストにある　→　納入リストのレコードと差異を確認してコピー
        else:
            #Sourceは作り直し
            s = ""
            for v in d.values():
                s = s + v + ","
            s = '"' + s[:-1] + '"'

            new_row.setdefault("CC_ID", row["CC_ID"])
            new_row.setdefault("BS_ID", row["BS_ID"])

            #郵便番号に差異なし　→　同じ装置と判定、緯度経度はそのまま
            if row['郵便番号'] == d['郵便番号']:
                new_row.setdefault("郵便番号", row["郵便番号"])
                new_row.setdefault("緯度", row["緯度"])
                new_row.setdefault("経度", row["経度"])

            #差異あり　→　違う装置と判定、緯度経度は取り直し
            else:
                #緯度、経度は取り直し
                location_target, postal_card = get_location(d['郵便番号'])
                time.sleep(1)  # リクエスト間に1秒待機
                if location_target == None:
                    writeLog("ERROR", f"get_location({d['郵便番号']}) -> 緯度、経度の取得に失敗しました：納入システム情報={s}")
                    continue
                new_row.setdefault("郵便番号", postal_card)
                new_row.setdefault("緯度", location_target.latitude)
                new_row.setdefault("経度", location_target.longitude)

            new_row.setdefault("Source", s)
        
        #更新先のレコードに登録
        updaete_db.append(new_row)

    for dev in devices:
        i_row +=1

        #進捗表示
        showProgress("DBを更新します：", i_row + 1, num_db + num_devices, 20)

        new_row = {}

        #DBに存在するレコードは無視
        d = searchTable(db, "CC_ID", dev['CC_ID'], "BS_ID", dev['BS_ID'])
        if d != None:
            continue

        #Source作成
        s = ""
        for v in dev.values():
            s = s + v + ","
        s = '"' + s[:-1] + '"'

        new_row.setdefault("CC_ID", dev["CC_ID"])
        new_row.setdefault("BS_ID", dev["BS_ID"])
        #緯度、経度
        location_target, postal_card = get_location(dev['郵便番号'])
        time.sleep(1)  # リクエスト間に1秒待機
        if location_target == None:
            writeLog("ERROR", f"get_location({dev['郵便番号']}) -> 緯度、経度の取得に失敗しました：納入システム情報={s}")
            continue 
        new_row.setdefault("郵便番号", postal_card)
        new_row.setdefault("緯度", location_target.latitude)
        new_row.setdefault("経度", location_target.longitude)
        new_row.setdefault("Source", s)

        #更新先のレコードに登録
        updaete_db.append(new_row)

    #進捗表示
    showProgress("DBを更新します：", i_row + 1, num_db + num_devices, 20)
    print()

    with open(g_DB_devicelist_file, "w", encoding="utf-8") as f:
        print("CC_ID,BS_ID,郵便番号,緯度,経度,Source", file=f)
        
        for u in updaete_db:
            s = ""
            for v in u.values():
                s = s + str(v) + ","
            print(s[:-1], file=f)
    print("...完了")

    return updaete_db



"""->
<-"""
def analyze(focaldatas, db, rad_km):
    print("震源地に近い装置を検索します：")
    print(f"　震源地からの距離 {rad_km}Km以内")
    bcp_devices = {}
    try:
        num_focaldatas = len(focaldatas)
        num_db = len(db)
        total = num_focaldatas * num_db
        i_row = -1
        j_focal = -1
        for focal in focaldatas:
            j_focal +=1

            lat_focal = float(focal["Latitude"])
            lon_focal = float(focal["Longitude"])

            for device in db:
                i_row +=1

                bs_id = device['BS_ID']
                lat_device = device['緯度']
                lon_device = device['経度']
            
                d_km = geodesic((lat_device, lon_device), (lat_focal, lon_focal)).km

                if d_km <= rad_km:
                    buflist = [int(d_km), focal["震央地名"], lat_focal, lon_focal, device] #距離(Km),震央地名,震源地緯度,震源地経度
                    if bs_id in bcp_devices.keys():
                        bcp_devices[bs_id].append(buflist)
                    else:
                        bcp_devices.setdefault(bs_id, [buflist])

                #進捗表示
                showProgress("進捗：", i_row + 1, total, 20)
        
        #進捗表示
        showProgress("進捗：", i_row + 1, total, 20)
        print()

        #結果出力
        with open(g_devicechecklist_file, "w", encoding="sjis") as f:
            print("CC_ID,顧客名,BS_ID,システム名,距離(Km),震央地名,震源地緯度,震源地経度,Source", file=f)
        
            for bs_id in bcp_devices.keys():
                for buflist in bcp_devices[bs_id]:
                    try:
                        device = buflist[4]
                        source = device['Source']
                        source_item = source.split(",")
                        customer_name = source_item[8]
                        system_name = source_item[2]
                        buf1 = f"{device['CC_ID']},{customer_name},{bs_id},{system_name},{buflist[0]},{buflist[1]},{buflist[2]},{buflist[3]},{device['Source']}"
                        print(f"{filter_sjis_compatible(buf1)}", file=f)
                    except Exception as e:
                        writeLog("ERROR", f"データの書き込みに失敗しました：BS_ID={bs_id}, エラー={e}")
                        continue

        print(rf"結果を出力しました  file: {g_devicechecklist_file}")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

def showFocalonMap(focaldatas):
    ans = ask_yes_no("震源地を地図で確認しますか？ Yes -> y, No -> n > ")
    if ans == False:
        return
    
    focal_map.show(focaldatas)

def ask_yes_no(question):
    while True:
        response = input(question ).strip().lower()  # ユーザーの入力を取得
        if response in ['y']:  # Yesの入力を処理
            return True
        elif response in ['n']:  # Noの入力を処理
            return False
        else:
            print("無効な入力です")

def ask_you(question, keys):
    while True:
        response = input(question ).strip().lower()  # ユーザーの入力を取得
        if response in keys:  # Yesの入力を処理
            return response
        else:
            print("無効な入力です")

def filter_sjis_compatible(text):
    return text.encode('shift_jis', errors='ignore').decode('shift_jis')

def main():
    
    #
    print("***********************************************************************************")
    print("*                                                                                 *")
    print("* BCPツール Ver 1.0.0                                                              *")
    print("*   Copyright © 2025 SMD                                                          *")
    print("*                                                                                 *")
    print("***********************************************************************************")

    ans = ask_you("解析モード？ 0:新規解析　1:再解析 > ", ['0', '1'])
    if ans == '0':
        #震源地リストの読込み
        focaldatas = loadFocalPointList()
        #地図
        showFocalonMap(focaldatas)
        #DB納入リストの読込み
        db = DBLoadDeviceList()
        #納入リストの読込み
        devices = LoadDeviceList()
        #DB納入リストの更新
        db = UpdateDB(db, devices)
        #被災病院の抽出
        analyze(focaldatas, db, 30)
    elif ans == '1':
        #震源地リストの読込み
        focaldatas = loadFocalPointList()
        #地図
        showFocalonMap(focaldatas)
        #DB納入リストの読込み
        db = DBLoadDeviceList()
        #被災病院の抽出
        analyze(focaldatas, db, 30)
    return

if __name__=='__main__':

    # 実行フォルダ（main.pyがあるフォルダ）
    _main_path = os.path.dirname(os.path.abspath(__file__))

    #実行
    main()