import webbrowser
import sqlite3
import tkinter as tk
from tkinter import messagebox

def get_recipe_url_from_db(recipe_id: int) -> str | None:
    """
    楽天レシピIDからレシピURLを取得する
    
    """
    db_path = "./rakuten_recipe_all.db" # SQLiteデータベースのパス
    
    try:
        with sqlite3.connect(db_path) as conn: # データベースに接続
            cursor = conn.cursor() # カーソルを取得
            # SQLクエリを実行
            # sql_excel_csv.py で指定したテーブル名を使用
            # 例: "your_table"
            cursor.execute("SELECT recipeUrl FROM your_table WHERE recipeId = ?", (recipe_id,))
            result = cursor.fetchone() # 結果を取得
            return result[0] if result else None # レシピURLを返す
                
    except sqlite3.Error as e: # エラーが発生した場合
        print(f"Database error: {e}") # エラーメッセージを出力
        # エラーを呼び出し元に伝えるために例外を発生させる
        raise e 
        
def on_open_button_click():
    """
    [ ブラウザでレシピを確認 ] ボタンがクリックされた時の処理
    """
    recipe_id_str = entry_recipe_id.get() # レシピIDを取得
    if not recipe_id_str: # レシピIDが空の場合
        messagebox.showwarning("入力エラー", "レシピIDを入力してください。")
        return # 終了
    
    try: # レシピIDを整数に変換
        recipe_id = int(recipe_id_str) # 文字列を整数に変換
    except ValueError: # 変換できなかった場合
        messagebox.showwarning("入力エラー", "レシピIDは数字で入力してください。")
        return # 終了
    
    try: # レシピURLを取得
        recipe_url = get_recipe_url_from_db(recipe_id) # レシピURLを取得
        if recipe_url: # レシピURLが取得できた場合
            webbrowser.open(recipe_url) # レシピURLを開く
        else: # レシピURLが取得できなかった場合
            messagebox.showwarning("レシピが見つかりません", f"レシピID：{recipe_id}に対応するレシピが見つかりません。")
    except sqlite3.Error as e: # エラーが発生した場合
        messagebox.showerror("データベースエラー", f"データベースエラーが発生しました: {e}")
    except Exception as e: # 予期せぬエラーが発生した場合
        messagebox.showerror("エラー", f"予期せぬエラーが発生しました: {e}")

# === ↓↓↓ GUIの設定 ↓↓↓ ===
# メイン処理
if __name__ == "__main__":
    # メインウィンドウ
    root = tk.Tk()
    root.title("楽天レシピ")
    # ウィンドウサイズ
    root.geometry("300x175")
    # ウィンドウサイズを変更不可に
    root.resizable(False, False)
    # メインフレーム
    main_frame = tk.Frame(root, padx=20, pady=20)
    # メインフレームを中央に配置 
    main_frame.pack(fill=tk.BOTH, expand=True)
    # ラベル
    label_instruction = tk.Label(main_frame, # 親フレーム
                                 text="レシピIDを入力してください", # ラベルのテキスト
                                 font=("Yu Gothic", 12) # フォント
                                 ) 
    # ラベルをメインフレームに配置
    label_instruction.pack(pady=(0, 5))
    # レシピID入力フィールド
    entry_recipe_id = tk.Entry(main_frame,
                               width=20, # フィールドの幅
                               font=("Yu Gothic", 14) # フォント
                               )
    # レシピID入力フィールドをメインフレームに配置 
    entry_recipe_id.pack(pady=5) # pady
    # 起動時, レシピID入力フィールドにフォーカス 
    entry_recipe_id.focus_set() 
    # ボタン
    button_open = tk.Button(
                            main_frame, # 親フレーム
                            text=" ブラウザでレシピを確認 ", # ボタンのテキスト
                            bg="lightblue", # ボタンの背景色
                            font=("Yu Gothic", 14), # フォント
                            command=on_open_button_click # ボタンがクリックされた時の処理
                            )
     
    # ボタンをメインフレームに配置
    button_open.pack(pady=15) 
    # Enterキーを押したときに同じ処理を実行
    root.bind("<Return>", lambda event: on_open_button_click()) 
     
    # GUIのメインループ
    root.mainloop() 
# === ↑↑↑ GUIの設定 ↑↑↑ ===
    