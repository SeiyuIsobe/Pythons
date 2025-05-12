import os
import re
import targetaxedasn
from datetime import datetime

#---------------------
#      入力パラメータ
#
#解析目的のssl_request_log
TARGET_ssl_request_log = r"C:\Devs\Axeda\tsvr1\var\log\httpd\ssl_request_log-20250511"
#
#解析対象は？　全て=True、絞る=False
IS_TARGET_ALL = True
#
#結果出力先フォルダ
OUTPUT_CSV_PATH = r"C:\Devs\Python\Output\SslRequestLogAnalyzer"
#
#結果出力先ファイル名
OUTPUT_CSV_FILE = "ssl_request.csv"
#
#対象の期間は？　指定する=True、指定しない=False
IS_PERIOD = False
#
#IS_PERIOD = Trueの場合
#開始日時
START_PERIOD_DATE = "2025/4/23 00:00:00"
#終了日時
END_PERIOD_DATE = "2025/4/24 23:59:59"
#---------------------

# global
_main_path = ""
_output_csv = []
_logDictionary = {}

_filepath = TARGET_ssl_request_log
_outcsvpath = OUTPUT_CSV_PATH
_outcsvfile = OUTPUT_CSV_FILE
_isTargetAll = IS_TARGET_ALL

# 期間指定
_isPeriod = IS_PERIOD
_fromPeriod = datetime.strptime(START_PERIOD_DATE, "%Y/%m/%d %H:%M:%S")
_toPeriod = datetime.strptime(END_PERIOD_DATE, "%Y/%m/%d %H:%M:%S")
_dic_month = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}

# 正規表現
#    _reg_sessionID_userID = re.compile(r'\[[0-9a-zA-Z]+\t[0-9a-zA-Z]+\]')
#    _reg_sessionID = re.compile(r'(?<=\[)[0-9a-zA-Z]+(?=\t)')
_reg_date = re.compile(r'(?<=\[)+.+(?=\])')
_reg_axedasn = re.compile(r'(?<=&sn\=)+.+(?=&ow\=)')
_reg_ip = re.compile(r'(?<=\] )+.+(?= TLSv)')
_reg_cipher = re.compile(r'(?<= TLSv\d\.\d )+.+(?= "GET )')
_reg_cipher2 = re.compile(r'(?<= TLSv\d )+.+(?= "GET )')
_reg_tls = re.compile(r'(?<= TLSv)+.+(?= \w+(-|_))') #TLSv以降

def isTargetAxedaSN(log_str):
    if _isTargetAll:
        return True
    
    for sn in targetaxedasn._sms:
        if(re.search(f"&sn={sn}&ow=", log_str, flags=0)):
            return True
    return False

def getTargetAxedaSNParameters(line_str):
    #
    result = _reg_date.search(line_str)
    if result:
        date = result.group(0)
        date = date.replace(" ", ",'", 1)
        date = date.replace(":", " ", 1)
    else:
        date = ""
    #
    result = _reg_ip.search(line_str)
    if result:
        ip = result.group(0)
    else:
        ip = ""
    #
    result = _reg_axedasn.search(line_str)
    if result:
        axedasn = result.group(0)
    else:
        axedasn = ""
    #
    result = _reg_tls.search(line_str)
    if result:
        tls = f"TLSv{result.group(0)}"
    else:
        tls = ""
    #
    result = _reg_cipher.search(line_str)
    if result:
        cipher = result.group(0)
    else:
        result2 = _reg_cipher2.search(line_str)
        if result2:
            cipher = result2.group(0)
        else:
            cipher = ""
    
    return date, ip, axedasn, tls, cipher

# 対応書式：01/Aug/2024:09:15:34
def getDateObject(line):
    try:
        d0 = re.split('[/: ,]', line)
        return datetime(
            int(d0[2]),
            _dic_month[d0[1]],
            int(d0[0]),
            int(d0[3]),
            int(d0[4]),
            int(d0[5])
            )
    except Exception as e:
        print(f"except!!! {e} -> {line}")

    return datetime(1900, 1, 1, 0, 0, 0, 0)

def isPeriod(date):
    #期間指定なし
    if(_isPeriod == False):
        return True
    
    #日付型に変換
    obj_date = getDateObject(date)
    
    if(_fromPeriod <= obj_date <= _toPeriod):
        return True
    
    return False
    
    
def read_ssl_request_log():
    global _output_csv

    print(f"読込ファイル：{_filepath}")
    print("")
    
    #ファイル読込
    c0 = 0
    cp = 0
    fr = open(fr"{_filepath}", encoding="utf-8")
    for line in fr:
        c0 = c0 + 1
        result = re.search("GET /lwPing\?id=", line, flags=0)
        if(result):
            cp = cp + 1
            print(f"\033[A{cp}")
            if(isTargetAxedaSN(line)):
                date, ip, axedasn, tls, cipher = getTargetAxedaSNParameters(line)
                if(isPeriod(date)):
                    if axedasn != "":
                        csv_string = f"{date},{ip},{axedasn},{tls},{cipher}"
                        try:
                            _logDictionary[axedasn].append(csv_string)
                        except:
                            _logDictionary.setdefault(axedasn, [csv_string])
            else:
                pass
        else:
            pass
    fr.close()
    print(f"全行数={c0}")
    print(f"　行数={cp}")
    print("")
            
    #ファイル書込
    i = 0
    count_axedasn = len(_logDictionary)
    for axedasn, dic_value in _logDictionary.items():
        outfile = fr"{_outcsvpath}\{axedasn}_{_outcsvfile}"
        with open(outfile, mode="w", encoding="utf-8") as f:
            i = i + 1
            print("datetime,timezone,IP,Axeda S/N,TLS,Cipher", file=f)
            for csv_string in dic_value:
                rr = int(i/count_axedasn*100)
                print(csv_string, file=f)
                print(f"\033[Aprogrss={rr}%")

    print("終了しました")

def main():
    if(_isTargetAll):
        print("全てのAxeda S/Nを探索します")
    else:
        print(f"{len(targetaxedasn._sms)}件のAxeda S/Nを探索します")
    
    if(_isPeriod):
        print(f"期間指定あり：{_fromPeriod}～{_toPeriod}")
    else:
        print("期間指定なし")
        
    read_ssl_request_log()

    

if __name__=='__main__':

    # 実行フォルダ（main.pyがあるフォルダ）
    _main_path = os.path.dirname(os.path.abspath(__file__))

    main()
