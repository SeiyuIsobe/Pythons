import os
import re
import csv
from collections import defaultdict
from datetime import datetime
import time

"""
[04/Jan/2024:05:43:03 +0900] 114.152.126.184 TLSv1.2 AES128-SHA "POST /eMessage HTTP/1.1" 265
"""

#---------------------
#      入力パラメータ
#
#解析目的のssl_request_log
TARGET_ssl_request_log = r"C:\Devs\TW\tw-cnn1\var\log\httpd\ssl_request_log"
#TARGET_ssl_request_log = r"C:\Devs\Python\GitHub\Pythons\SslRequestCounter\test\ssl_request_log"
#結果出力先フォルダ
OUTPUT_CSV_PATH =  r"C:\Devs\Python\GitHub\Pythons\SslRequestCounter"
#
#結果出力先ファイル名
OUTPUT_CSV_FILE = "ssl_request_count.csv"
#
#特定時間解析
#TARGET_DATE = None #特定しない場合
TARGET_DATE = datetime.strptime("2026/2/12", "%Y/%m/%d")
TARGET_HOUR = 11
STEP_NUMBER = 5
#---------------------

# global
_main_path = ""
_output_csv = []
_logDictionary = {}
_outcsvpath = OUTPUT_CSV_PATH
_outcsvfile = OUTPUT_CSV_FILE
_target_date = TARGET_DATE
_target_hour = TARGET_HOUR
_step_number = STEP_NUMBER
_step_list = []

_filepath = TARGET_ssl_request_log
# カウント用辞書
_counter = defaultdict(lambda: {'GET': 0, 'POST': 0})

def createStep():
    ss = 60 / _step_number
    step_list = []
    for i in range(int(ss)):
        step_list.append(_step_number*(i))
    return step_list

def min_step(min):
    global _step_list

    nn = int(60/_step_number)-1
    for i in range(nn):
        if _step_list[i] <= min and min < _step_list[i+1]:
            return _step_list[i]
    return _step_list[int(60/_step_number)-1]

def checkTarget(year, mon, day, hour):
    if _target_date is None:
        return (False, False)
    else:
        d = datetime.strptime(f"{year}/{mon}/{day}", "%Y/%m/%d")
        dd = d - _target_date
        if dd.days == 0 and hour == _target_hour:
            return (True, True)
        else:
            return (True, False)

def read_ssl_request_log():
    global _output_csv
    global _step_list

    _step_list = createStep()

    # ログのパターン
    #   ()で囲むことにより抽出する　→　日、月、年、時、分、メソッドの順番で抽出
    log_pattern = re.compile(
        r"(\d{2})/(\w{3})/(\d{4}):(\d{2}):(\d{2}):\d{2} [+\-]\d{4}.*?\"(GET|POST)"
    )

    # 月の英語表記を数値に変換
    month_map = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
    }

    print(f"読込ファイル：{_filepath}")
    print("")
    
    #ファイル読込
    c0 = 0
    cp = 0
    fr = open(fr"{_filepath}", encoding="utf-8")
    for line in fr:
        c0 = c0 + 1
        m = log_pattern.search(line)
        if m:
            day, mon_str, year, hour, min, method = m.groups()
            min = min_step(int(min)) # 分は特定期間にまとめる
            mon = month_map[mon_str]
            date_str = f"{year}/{mon}/{int(day)}"
            hour = int(hour)

            isTarget, isEnabeled = checkTarget(year, mon, int(day), hour)

            if isTarget:
                if isEnabeled:
                    _counter[(date_str, hour, min)][method] += 1
            else:
                _counter[(date_str, hour, min)][method] += 1
            
            
    fr.close()
    print(f"全行数={c0}")
    print(f"　行数={cp}")
    print("")
            
    # 出力
    output_lines = []
    header = ['"yyyy/mm/dd"', '"Hour"', '"Minute"', '"GET"', '"POST"']
    output_lines.append(','.join(header))

    # 対象日と時間を抽出（存在するデータのみ出力）
    dates = set(date for (date, hour, min) in _counter.keys())

    if _target_date is None:

        for date in sorted(dates):
            for hour in range(24):
                get_cnt = _counter.get((date, hour), {}).get('GET', 0)
                post_cnt = _counter.get((date, hour), {}).get('POST', 0)
                output_lines.append(f'"{date}", {hour}, {get_cnt}, {post_cnt}')

    else:
        date = f"{_target_date.year}/{_target_date.month}/{_target_date.day}"
        for min in _step_list:
            get_cnt = _counter.get((date, _target_hour, min), {}).get('GET', 0)
            post_cnt = _counter.get((date, _target_hour, min), {}).get('POST', 0)
            output_lines.append(f'"{date}",{_target_hour},{min},{get_cnt},{post_cnt}')




    # 結果表示（ファイル保存の場合はcsv.writerを使ってください）
    with open(fr"{_outcsvpath}\{_outcsvfile}", mode="w", encoding="utf-8") as f:
        for line in output_lines:
            print(line, file=f)

    print("終了しました")

def main():
    read_ssl_request_log()

if __name__=='__main__':

    # 実行フォルダ（main.pyがあるフォルダ）
    _main_path = os.path.dirname(os.path.abspath(__file__))

    # 計測開始
    start_time = time.time()

    main()

    # 計測終了
    end_time = time.time()
    print(f"処理時間: {end_time - start_time:.2f}秒")