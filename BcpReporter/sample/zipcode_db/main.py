from zipcode_db import ZipcodeDB

db = ZipcodeDB("zipcode_location.csv")

def aaa():
    db.add_or_update("1000003", 135.687456, 39.760837)
    
def main():
    

    # 追加・更新
    db.add_or_update("1000001", 35.684063, 139.754344)
    db.add_or_update("1000002", 35.687456, 139.760837)

    # 検索（namedtupleで受け取る）
    info = db.get("1000001")
    if info:
        print(f"郵便番号: {info.postal_code}, 緯度: {info.latitude}, 経度: {info.longitude}")
    else:
        print("該当なし")

    # 全件表示
    print("全件一覧:")
    print(db.list_all())

    # 削除
    db.remove("1000002")
    print("削除後:")
    print(db.list_all())

    aaa()
    print(db.list_all())
    
if __name__ == "__main__":
    main()
