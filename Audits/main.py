"""
ThingWorx/Composer/ExportOnlineAuditData
上記APIから出力されるファイルを読込み、SMS用のフォーマットに整形する

改訂履歴：
2025/10/07  jsonファイルを探索するロジックの変更
            SMSの要求するCategoryに変更する機能の追加
"""
import json
import glob
from datetime import datetime
import pathlib

"""
{
    "rows": [
        {
            "auditCategory": "File Transfer",
            "application": "ThingWorxCore",
            "sourceType": "Thing",
            "source": "TWL00837",
            "message": "File transfer from: TWL00837/20250113T171935.731Z-d7e7b1a0-2cc3-4c59-b5dc-dc68b8f6e1e9.tar.gz to SMZ.FilesFromAsset.FR/20250113T171935.731Z-d7e7b1a0-2cc3-4c59-b5dc-dc68b8f6e1e9.tar.gz. State=ACTIVE",
            "user": "eMessageConnectorUser",
            "timestamp": 1736788776006
        }
    ]
}
"""


# 定義
#TARGET_JSON = r"C:\Users\s-iso\Downloads\sms_202504_202509\AuditArchive\AuditArchiveDirectPersistence\export\*.json"
TARGET_JSON = r"C:\temp\temp6\*.json"
TARGET_ROOT = r"C:\temp\temp6\out"
OUTPUT_CSV = "audit_log_all_test.csv"
IS_SOURCE_TWL = True # sourceがThingNameであるもののみ抽出=True、全部=False

_dic_cat = {
    "IDM WS Extension": "Information",
    "Maintenance Window": "Information",
    "User Alerts": "Information",
    "Alarm Acknowledge": "Loｗ",
    "Asset Communication": "Medium",
    "Code Access Policy": "Information",
    "Custom": "Information",
    "Custom Object": "Information",
    "Custom Object Group": "Information",
    "Data Export": "Critical",
    "Data Management": "Medium",
    "Data Streaming": "Information",
    "Extended Data": "Information",
    "External Credential": "High",
    "File Transfer": "Low",
    "File Upload": "Low",
    "Maintenance": "Medium",
    "Network": "Medium",
    "Package Management": "Information",
    "Partner Login": "High",
    "Remote Access": "Critical",
    "Rules Configuration": "Medium",
    "Scripting": "Critical",
    "System Configuration": "Medium",
    "Transport ServiceLink": "Information",
    "User Access": "High",
    "Modeling": "Medium"
}

def getLogFileList(pt, ext):
    path = pathlib.Path(pt)
    files = path.glob(ext)
    return files

def convertForSMSCategory(fromCat):
    try:
        val = _dic_cat[fromCat]
        return val
    except:
        pass
    return None

def main():
    
    #JSONファイルのリスト取得
    #jsons = glob.glob(TARGET_JSON)
    jsons = getLogFileList(TARGET_ROOT, "**/*.json")


    
    try:
        #ヘッダーの書込み
        fheader = open(OUTPUT_CSV, "w") #既存をクリアのモード
        fheader.writelines("timestamp(UTC),Cat,Category,Description,user,Asset,不要,不要\n")
        fheader.writelines("timestamp(UTC),,auditCategory,message,user,source,application,sourceType\n") #変換後が分かるように残すため
        fheader.close()
    
    except Exception as e3:
        print(e3)
        

    #全ファイル
    for json_file in jsons:
    
        try:
            #JSONファイルの読込み
            f = open(json_file, encoding='utf-8')
            
            #JSON形式に変換
            json_data = json.load(f)
            
            #クローズ
            f.close()
            
            try:
                #CSVファイルに書込み
                fw = open(OUTPUT_CSV, "a") #既存に追加のモード                
            
                #全行書出し
                for row in json_data["rows"]:
                    #書出し条件
                    if IS_SOURCE_TWL:
                        if row["source"].startswith("TWL"):
                            isOut = True
                        else:
                            isOut = False
                    else:
                        isOut = True

                    if isOut:
                        fw.writelines("{0},{1},{2},{3},{4},{5},{6},{7}\n".format(
                            datetime.fromtimestamp(row["timestamp"]/1000), #unixtimeは1000で割る
                            convertForSMSCategory(row["auditCategory"]),
                            row["auditCategory"],
                            row["message"],
                            row["user"],
                            row["source"],
                            row["application"],
                            row["sourceType"]
                            )
                        )
                    
                #書込み先のクローズ
                fw.close()
                
            except Exception as ee:
                print(ee)
                
           
            
        except Exception as e:
            print(e)
    
    

if __name__=='__main__':
    main()