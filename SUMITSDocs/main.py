import os
import re
import html
import pathlib
from bs4 import BeautifulSoup

"""
SUMITSのドキュメント一覧画面をローカルに保存（ブラウザの拡張機能：Singlefile）
SUMITSの一覧表画面はiframeで分割されている
iframeは3つある
iframeのブロックをファイルに出力する
　→一覧表
"""

TARGET_ROOT = r"C:\temp\temp3\sumits_out"
EXPORT_ROOT = r"C:\temp\temp3\export"

_rx_iframe_block = re.compile(r'(?<=<iframe).*?(?=/iframe>)')
_rx_srcdoc = re.compile(r'(?<=srcdoc=\").*?(?=\"><)')

def getFileList(pt, ext):
    path = pathlib.Path(pt)
    files = path.glob(ext)
    return list(files)

def get_srcdoc(str_html, str_fix):
    ret = _rx_srcdoc.findall(str_html)
    if len(ret) > 0:
        return ret[0] + str_fix
    
    return None

def main():
    lst_table = []
    first_soup = None

    files = getFileList(TARGET_ROOT, "**/*.html")
    for file in files:
        print(f"処理中：{file}...", end="")

        # ファイル名を取り出す
        file_name = os.path.basename(file)

        input_file_path = str(file)
        output_file_path = rf"{EXPORT_ROOT}\ex_{file_name}"

        soup, tbl_sublist1 = analyze(input_file_path, output_file_path)
    
        #最初の一つ目だけ保持
        if first_soup == None:
            first_soup = soup

        #追加
        lst_table.append(tbl_sublist1)

        print("ok")

    #tableをマージ
    #最初のtable抽出
    first_tbl_sublist1 = first_soup.find('table', id='SubList1')

    print(f"抽出完了　テーブル数：{len(lst_table)}")

    for i in range(len(lst_table)-1):
        ex_tbl = lst_table[i+1]
        # ex_tblの内容をtblに追加
        if first_tbl_sublist1 and ex_tbl:
            # ex_tblの中の行をすべてtblに追加
            for row in ex_tbl.find_all('tr'):
                first_tbl_sublist1.append(row)
    
    # 新しいHTMLを作成
    output_file_path = rf"{EXPORT_ROOT}\ss.html"
    with open(output_file_path, 'w', encoding='utf-8') as outfile:
        outfile.write(first_tbl_sublist1.prettify()) 

    return

def analyze(input_path, output_path):
    
    try:
        # ファイルを読み込む
        with open(input_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

            #sample
            #ll = '<td id=col_menu' + "\n" + 'class=frameBase style=width:300px><iframe id=menu name=menu class=frameBase title=menu sandbox="allow-popups allow-top-navigation-by-user-activation" srcdoc="<!DOCTYPE html> </div></form>"></iframe></td>'
            #iframes = _rx_iframe_block.findall(ll)

            # <iframe ... </iframe> を正規表現で抽出（複数行対応）
            #iframeは3つある、左メニュー、本体、空白？
            #目的のiframeにはid=SearchConditionを持つtableがある
            html_content = html_content.replace('\n', '') #改行コードにより正規表現が失敗するので削除
            iframes = _rx_iframe_block.findall(html_content)

            # 抽出したiframeタグをファイルに書き出す
            i = 1
            for iframe in iframes:
                #iframeの属性srcdocの内容を取得
                srcdoc = get_srcdoc(iframe, "</body></html>")
                if srcdoc != None:
                    #目的のiframe
                    if "id=SearchCondition" in srcdoc:
                        #HTMLエンコードをデコード
                        srcdoc = html.unescape(srcdoc)

                        #ファイル出力
                        #with open(output_path, 'w', encoding='utf-8') as f:
                        #    f.write(srcdoc)

                        #DOM化
                        soup = BeautifulSoup(srcdoc, 'html.parser')
                        #table抽出
                        tbl_sublist1 = soup.find('table', id='SubList1')
                        
                i = i+1
        
        return soup, tbl_sublist1

    except Exception as e:
        print(e)
    
if __name__=='__main__':

    # 実行フォルダ（main.pyがあるフォルダ）
    _main_path = os.path.dirname(os.path.abspath(__file__))

    main()