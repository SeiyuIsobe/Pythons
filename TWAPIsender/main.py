import os
import requests
import json
import time

# REST APIのURL
#url = "https://tw-tsvr1.md.shimadzu.co.jp/Thingworx/Things/TEST0001/Services/UpdatePropertyValues"
url = "https://tw-tsvr1.md.shimadzu.co.jp/Thingworx/Things/TEST0001/Properties/"


mode = "test"

dic_url = {
    "test":"https://tw-tsvr1.md.shimadzu.co.jp",
    "prod":"https://tw-svr1.md.shimadzu.co.jp"}

#mode = "prod"

# JSONファイルのパス
json_file_path = "post_data.json"

# ヘッダー情報（必要に応じて調整）
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "appKey": "d371da30-24ff-4812-8721-acd178da2dc4"
    # "Authorization": "Bearer YOUR_ACCESS_TOKEN"  # 認証が必要な場合はここに追加
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

def main():
    #register()

    test2()
    
if __name__=='__main__':

    # 実行フォルダ（main.pyがあるフォルダ）
    _main_path = os.path.dirname(os.path.abspath(__file__))

    main()
