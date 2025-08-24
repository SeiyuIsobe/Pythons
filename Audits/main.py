import json
import glob
from datetime import datetime

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
#TARGET_JSON = r"C:\Users\s-iso\Downloads\TWL00837_241001_250331_all\AuditArchive\AuditArchiveDirectPersistence\export\*.json"
#TARGET_JSON = r"AuditArchive\AuditArchiveDirectPersistence\export\*.json"
TARGET_JSON = r"C:\temp\temp5\act2\AuditArchive\AuditArchiveDirectPersistence\export\*.json"
OUTPUT_CSV = "audit_log.csv"
IS_SOURCE_TWL = True # sourceが入っているもののみ抽出=True

def main():
    
    #JSONファイルのリスト取得
    jsons = glob.glob(TARGET_JSON)
    
    try:
        #ヘッダーの書込み
        fheader = open(OUTPUT_CSV, "w") #既存をクリアのモード
        fheader.writelines("auditCategory,application,sourceType,source,message,user,timestamp(UTC)\n")
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
                        fw.writelines("{0},{1},{2},{3},{4},{5},{6}\n".format(
                            row["auditCategory"],
                            row["application"],
                            row["sourceType"],
                            row["source"],
                            row["message"],
                            row["user"],
                            datetime.fromtimestamp(row["timestamp"]/1000) #unixtimeは1000で割る
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