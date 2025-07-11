import pandas as pd
import sqlite3 # SQLiteをインポート

# CSVまたはExcelファイルを読み込む
# --- ↓↓↓ ファイルの拡張子によって切り換える ↓↓↓ --
# CSVファイルのパスを指定
csv_path = ("./ファイル名.csv")
# Excelファイルのパスを指定
# df = pd.read_excel("./ファイル名")
# ----------------------------------------------

# SQLiteのデータベースを指定（存在しない場合は作成される）
db_path = "./データベース名.db"

# 正しいエンコーディングを指定してCSVを読み込む
# 例えば、'latin1'や'cp932'を試してみる
try:
    df = pd.read_csv(csv_path, encoding="utf-8") 
except UnicodeDecodeError:
    df = pd.read_csv(csv_path, encoding="latin1")

# データベースへの接続を確立
conn = sqlite3.connect(db_path)

# データフレームをデータベースに書き込む
df.to_sql("your_table", conn, if_exists="replace", index=False) 
# 接続を閉じる
conn.close()
 
print("エクスポート完了")