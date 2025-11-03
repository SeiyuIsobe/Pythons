import os
import requests
import json
import time
from datetime import datetime, timezone

# REST APIのURL
#url = "https://tw-tsvr1.md.shimadzu.co.jp/Thingworx/Things/TEST0001/Services/UpdatePropertyValues"
url = "https://tw-tsvr1.md.shimadzu.co.jp/Thingworx/Things/TEST0001/Properties/"


#mode = "test"
mode = "prod"

dic_url = {
    "test":"https://tw-tsvr1.md.shimadzu.co.jp",
    "prod":"https://tw-svr1.md.shimadzu.co.jp"}

dic_appkey = {
    "test":"d371da30-24ff-4812-8721-acd178da2dc4",
    "prod":"f2a13a3a-93b0-4f1e-a76e-54f68655ca94"
}

# JSONファイルのパス
json_file_path = "post_data.json"

# ヘッダー情報（必要に応じて調整）
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    #"appKey": "d371da30-24ff-4812-8721-acd178da2dc4"
    "appKey": dic_appkey[mode]
}

def loadPayload(file_path):
    try:
        with open(file_path, "r") as file:
            payload = json.load(file)  # JSONデータを辞書型に変換
    except FileNotFoundError:
        print(f"エラー: {file_path} ファイルが見つかりません。")
        exit()
    except json.JSONDecodeError:
        print(f"エラー: {file_path} の内容が正しいJSON形式ではありません。")
        exit()
    
    return payload

def CreateAsset():
    url = f"{dic_url[mode]}/Thingworx/Things/SMZ.AssetEdit.MSRV/Services/CreateAsset"
    payload = loadPayload("CreateAsset.json")

    try:
        r = requests.post(url, headers=headers, data=json.dumps(payload))

        # レスポンスのステータスコードと内容を表示
        print(f"CreateAsset: {r.status_code}")
        #print("レスポンス内容:")
        #print(r.text)
    except requests.exceptions.RequestException as e:
        print(f"エラーが発生しました: {e}")

def SetPaging():
    url = f"{dic_url[mode]}/Thingworx/Things/SMZ.AssetManagement.MSRV/Services/SetPaging"
    payload = loadPayload("CreateAsset.json")

    try:
        r = requests.post(url, headers=headers, data=json.dumps(payload))

        # レスポンスのステータスコードと内容を表示
        print(f"SetPaging: {r.status_code}")
        #print("レスポンス内容:")
        #print(r.text)
    except requests.exceptions.RequestException as e:
        print(f"エラーが発生しました: {e}")

def SetResultNumber():
    url = f"{dic_url[mode]}/Thingworx/Things/SMZ.Common.MSRV/Services/SetResultNumber"
    payload = loadPayload("SetResultNumber.json")

    try:
        r = requests.post(url, headers=headers, data=json.dumps(payload))

        # レスポンスのステータスコードと内容を表示
        print(f"SetResultNumber: {r.status_code}")
        #print("レスポンス内容:")
        #print(r.text)
    except requests.exceptions.RequestException as e:
        print(f"エラーが発生しました: {e}")

def ExportOnlineAuditData():
    url = f"{dic_url[mode]}/Thingworx/Subsystems/AuditSubsystem/Services/ExportOnlineAuditData"

"""
ThingWorxに新しいアセットを登録する
登録にはTW_api.xlsmにて以下のjsonを作成しておく
・CreateAsset.json
・SetPasing.json
・SetResultNumber.json
"""
def register():
    CreateAsset()
    time.sleep(1)  # リクエスト間に1秒待機
    SetPaging()
    time.sleep(1)  # リクエスト間に1秒待機
    SetResultNumber()

def test2():
    url = f"{dic_url[mode]}/Thingworx/Things/SMD001/Services/UpdatePropertyValues"
    payload = loadPayload("error_Message.json")

    try:
        r = requests.post(url, headers=headers, data=json.dumps(payload))

        # レスポンスのステータスコードと内容を表示
        print(f"ステータスコード: {r.status_code}")
        print("レスポンス内容:")
        print(r.text)
    except requests.exceptions.RequestException as e:
        print(f"エラーが発生しました: {e}")

def test():
    url = f"{dic_url[mode]}/Thingworx/Things/TEST0001/Properties/"
    try:
        r = requests.get(url, headers=headers)

        # レスポンスのステータスコードと内容を表示
        print(f"ステータスコード: {r.status_code}")
        print("レスポンス内容:")
        print(r.text)
    except requests.exceptions.RequestException as e:
        print(f"エラーが発生しました: {e}")

def exec_UpdatePropertyValues(sleep_time, thingname, formated_time, level_item, level_value, message_item, message_value):
    url = f"{dic_url[mode]}/Thingworx/Things/{thingname}/Services/UpdatePropertyValues"
    payload = loadPayload("payload_updatepropertyvalues.json")

    values_data = payload["values"]
    rows_data = values_data["rows"]
    level_data = rows_data[0]
    message_data = rows_data[1]

    level_data["name"] = level_item
    level_data["time"] = formated_time
    level_data["value"] = level_value

    message_data["name"] = message_item
    message_data["time"] = formated_time
    message_data["value"] = message_value

    try:
        f = open("result.txt", encoding="utf-8", mode="a")

        print(f"{thingname}\t", end="", file=f)
        r = requests.post(url, headers=headers, data=json.dumps(payload))

        if(str(r.status_code) in "200"):
            #POST/Alarm/Mail/Content
            print(f"OK\t?\t?\t?\t{level_item}\t{level_value}\t{message_item}\t{message_value}", file=f)
        else:
            print(f"NG\tN/A\tN/A\tN/A\t{level_item}\t{level_value}\t{message_item}\t{message_value}", file=f)

        # レスポンスのステータスコードと内容を表示
        #print(f"ステータスコード: {r.status_code}")
        #print("レスポンス内容:")
        #print(r.text)

        if(sleep_time > 0):
            time.sleep(sleep_time)

    except requests.exceptions.RequestException as e:
        print(f"エラーが発生しました: {e}")

    f.close()

    return

def get_current_datetime_iso():
    # 現在のUTC日時を取得
    current_time = datetime.now(timezone.utc)
    # 指定された形式にフォーマット
    formatted_time = current_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    return formatted_time

def tester():
    exec_UpdatePropertyValues(1, "TEST2509171", get_current_datetime_iso(), "ISYS_F_Error_Level", 5, "ISYS_F_Error_Message", "FPD Cooling unit error detected.")

def main():
    #register()

    #test2()

    tester()

    



    
if __name__=='__main__':

    # 実行フォルダ（main.pyがあるフォルダ）
    _main_path = os.path.dirname(os.path.abspath(__file__))

    main()
