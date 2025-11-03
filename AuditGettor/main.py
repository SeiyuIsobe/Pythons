import os

"""
起動時の確認メッセージの表示
"""
def ShowOoeningMessage():
    import tkinter as tk
    from tkinter import ttk, messagebox
    from tkcalendar import DateEntry

    # OKボタンが押されたとき
    def on_ok():
        date_value = date_entry.get_date().strftime("%Y-%m-%d")
        option_value = combo.get()
        messagebox.showinfo("入力結果", f"日付: {date_value}\n選択: {option_value}")

    # キャンセルボタンが押されたとき
    def on_cancel():
        root.destroy()

    # メインウィンドウ作成
    root = tk.Tk()
    root.title("ThingWorx監査ログエクスポート設定フォーム")
    root.geometry("640x480")

    # エクスポートの範囲：開始日を選択　／カレンダー
    tk.Label(root, text="エクスポートの範囲 - 開始日を選択：").pack(pady=(10, 0))
    date_entry = DateEntry(root, date_pattern="yyyy-mm-dd")
    date_entry.pack(pady=5)

    # エクスポートの範囲：期間を選択　／ドロップダウンリスト
    tk.Label(root, text="エクスポートの範囲 - 期間を選択：").pack(pady=(10, 0))
    term_export_combo = ttk.Combobox(root, values=["一か月", "一週間", "一日"])
    term_export_combo.current(0)
    term_export_combo.pack(pady=5)
    
    # 対象国　／ドロップダウンリスト
    tk.Label(root, text="対象国:").pack(pady=(10, 0))
    target_country_combo = ttk.Combobox(root, values=["（未選択）", "All", "USA"])
    target_country_combo.current(0)
    target_country_combo.pack(pady=5)

    # ボタンエリア
    frame_buttons = tk.Frame(root)
    frame_buttons.pack(pady=15)

    tk.Button(frame_buttons, text="OK", width=10, command=on_ok).pack(side="left", padx=5)
    tk.Button(frame_buttons, text="キャンセル", width=10, command=on_cancel).pack(side="right", padx=5)

    root.mainloop()
    
def main():
    
    # 起動時の確認メッセージの表示
    ShowOoeningMessage()
    
if __name__=='__main__':

    # 実行フォルダ（main.pyがあるフォルダ）
    _main_path = os.path.dirname(os.path.abspath(__file__))

    #実行
    main()