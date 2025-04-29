import os
import re
import targetaxedasn

# global
_main_path = ""
_output_csv = []
_logDictionary = {}

_filepath = r"C:\Devs\TW\tw-cnn1\var\log\httpd\ssl_request_log-20250420"
#_filepath = r"..\_data\ssl_request_log-20250420"
_outcsvpath = r"..\_out\ssl_request"
_outcsvfile = "ssl_request.csv"
_isTargetAll = False



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
    read_ssl_request_log()

    

if __name__=='__main__':

    # 実行フォルダ（main.pyがあるフォルダ）
    _main_path = os.path.dirname(os.path.abspath(__file__))

    main()
