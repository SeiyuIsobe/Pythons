import os
import re
import pandas as pd
from geopy.geocoders import Nominatim
from haversine import haversine
import time
import csv
from geopy.distance import geodesic
from datetime import date
from collections import namedtuple

# ジオロケーターの初期化
geolocator = Nominatim(user_agent="myGeocoder")

# 位置情報の構造体を定義
Location = namedtuple("Location", ["latitude", "longitude"])

def get_location(postal_code, retries=10):
    if ',' in postal_code:
        try:
            # 郵便番号がカンマ区切りの場合は最初の部分を使用
            return Location(postal_code.split(',')[0], postal_code.split(',')[1]), None
        except:
            return None, None
        
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

# 郵便番号をハイフン付きに変換する関数
def format_postal_code(postal_code):
    try:
        if len(postal_code) == 7 and postal_code.isdigit():
            return f"{postal_code[:3]}-{postal_code[3:]}"
        return postal_code
    except:
        return None
    
location_target, postal_card = get_location("1.1, 2.24")
print(f"{location_target.latitude}, {location_target.longitude}, {postal_card}")