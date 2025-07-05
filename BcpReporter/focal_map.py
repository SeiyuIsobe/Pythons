import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
import matplotlib.pyplot as plt
import csv

#データ
#東京ー大阪間：406.42km、271px　→　0.67px/km

g_width = 0
g_height = 0
g_lat_min, g_lon_min = 21.993036, 120.803206 #日本の左下
g_lat_max, g_lon_max = 46.215958, 150.395191 #日本の右上

# 緯度・経度を画像上の座標に変換する関数
def lat_lon_to_xy(lat, lon):
    # 緯度・経度を画像の座標に変換
    x = int((lon - g_lon_min) / (g_lon_max - g_lon_min) * g_width)
    y = int((g_lat_max - lat) / (g_lat_max - g_lat_min) * g_height)  # Y軸は上下反転
    return x, y

# 画像上の座標を位置情報から取得する関数
def xy_to_lat_lon(x, y):
    # 画像の座標を緯度・経度に変換
    lon = g_lon_min + (x / g_width) * (g_lon_max - g_lon_min)
    lat = g_lat_max - (y / g_height) * (g_lat_max - g_lat_min)  # Y軸は上下反転
    return lat, lon

# マーカーを描画する関数
def draw_marker(image, x, y, radius=30, thickness=2, color='red'):
    draw = ImageDraw.Draw(image)
    # 円を描画
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), outline=color, width=thickness)

def show(focaldatas):
    global g_width
    global g_height

    # 日本地図の画像を読み込む
    image_path = 'japan_map.jpg'  # 任意のサイズの日本地図のパス
    image = Image.open(image_path)

    # 画像の幅と高さを取得
    g_width, g_height = image.size

    # マーカーを描画する
    for focal in focaldatas:
        lat = float(focal["Latitude"])
        lon = float(focal["Longitude"])
        x, y = lat_lon_to_xy(lat, lon)
        #補正
        y = y - (0.00008*y*y-0.1358*y-3.9583)
        print(f"{x}, {y}")  # 座標を表示
        draw_marker(image, x, y, radius=10, thickness=5, color='red')
    
    # マーカーを描画した画像を表示
    plt.imshow(image)
    plt.axis('off')  # 軸を非表示にする
    plt.show()