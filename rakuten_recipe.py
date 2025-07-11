"""
楽天レシピAPIでカテゴリリストと人気ランキングを取得するヤツ
(APIの仕様により各カテゴリ4位までの人気レシピを自動取得)

Python 3.13.0
Gemini Code Assist
VSCode

"""

import requests
import pandas as pd 
import time 
import os
import sys
import logging # ログ出力用
from tqdm import tqdm # 進捗バー表示用

# スプリクトにおける絶対パス
scr_path = os.path.dirname(os.path.abspath(sys.argv[0]))

# --- ↓↓↓ 設定 ↓↓↓ ---
APPLICATION_ID = " APIキー" 
  # 取得した実際のAPIキーに置き換える
BASE_URL = "https://app.rakuten.co.jp/services/api/Recipe/"

# リストの最終更新は2017年4月26日
# カテゴリリスト
CATEGORY_LIST_API_URL = f"{BASE_URL}CategoryList/20170426"
# 人気ランキング 
CATEGORY_RANKING_API_URL = f"{BASE_URL}CategoryRanking/20170426"
# CSV出力ファイル
OUTPUT_CSV_PATH = os.path.join(scr_path, ".csv")
# APIリクエスト間の待機時間
REQUEST_WAIT_TIME = 3 
# ロガーの設定
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
# --- ↑↑↑ 設定 ↑↑↑ ---

def fetch_api_data(url: str, params: dict) -> dict | None: # 汎用関数
    """
    楽天APIからデータを取得する汎用関数

    param url: APIのエンドポイントURL
    param params: APIに渡すパラメータの辞書
    return: APIレスポンスのJSONデータ
    """
    try:
        # 共通パラメータ
        params["applicationId"] = APPLICATION_ID # 実際のAPIキー
        params["format"] = "json" # JSON形式
        
        response = requests.get(url, params=params) # APIリクエスト
        response.raise_for_status() # HTTPエラーがあれば例外を発生
        return response.json() # JSON形式のレスポンスを返す
    
    # APIリクエスト時の例外
    except requests.exceptions.RequestException as e: 
        print(f"An error occurred: {e}")
        logging.error(f"APIリクエストエラーが発生しました(URL: {url}, パラメータ: {params}): {e}") # ログ出力
        return None # 例外発生時はNoneを返す

def get_all_categories() -> pd.DataFrame:
    """
    楽天レシピのカテゴリを全取得し、DataFrameに格納する

    Returns:
    楽天レシピのカテゴリ情報を含むDataFrame
    """
    logging.info("カテゴリの一覧を取得します。") # ログ出力
    json_data = fetch_api_data(CATEGORY_LIST_API_URL, {}) # APIリクエスト 
    if not json_data or "result" not in json_data: # APIレスポンスの検証
        logging.error("楽天レシピのカテゴリ情報を取得できませんでした。レスポンス不正")
        return pd.DataFrame() # 空のDataFrameを返す
    
    categories = [] # カテゴリ情報を格納するリスト
    # 大・中・小カテゴリを取得する
    for category_type in ["large", "medium", "small"]: # 各カテゴリタイプ
        # レスポンスにカテゴリタイプが存在するかチェック
        if category_type in json_data.get("result", {}): # APIレスポンスの検証
            for category in json_data["result"][category_type]: # 各カテゴリを取得
                # 必須キー: categoryId, categoryName, categoryUrl
                if not all(k in category for k in ["categoryId", "categoryName", "categoryUrl"]): # APIレスポンスの検証
                    logging.warning(f"必須キー不足, カテゴリスキップ: {category}")
                    continue
                
                # CategoriRanking APIでレシピを取得するため, IDを生成
                # 中・小カテゴリの場合, "親ID・子ID" の関係となる
                parent_id = category.get("parentCategoryId") # 親カテゴリID
                full_category_id = f"{parent_id}-{category["categoryId"]}" if parent_id else str(category["categoryId"]) # 全カテゴリID
                
                # カテゴリ情報を格納
                categories.append({
                    "categoryId": full_category_id, # カテゴリID
                    "categoryName": category["categoryName"], # カテゴリ名
                    "categoryUrl": category["categoryUrl"] # カテゴリURL
                })
    
    logging.info(f"{len(categories)}件のカテゴリ情報を取得しました。")
    return pd.DataFrame(categories) # DataFrameに格納

def get_category_recipes(category_id: str) -> list: # 楽天レシピAPIから人気レシピを取得
    """
    指定されたカテゴリの人気レシピを取得
    
    params: category_id: 楽天レシピAPIから取得したカテゴリID
    return: 人気レシピの辞書リスト
    """
    params = {"categoryId": category_id} # APIに渡すパラメータ
    json_data = fetch_api_data(CATEGORY_RANKING_API_URL, params) # APIリクエスト    
    
    if not json_data or "result" not in json_data: # APIレスポンスの検証
        # 人気ランキングのため, レシピが少ないなどの理由でランキングが存在しないカテゴリがある
        # この場合はエラーではなく想定内の動作
        logging.info(f"カテゴリID：{category_id}に有効なランキングが存在しないためスキップ")
        return [] # 空のリストを返す
    
    recipes_data = [] # レシピ情報を格納するリスト
    for recipe in json_data["result"]: # 各レシピ
        # 材料リスト: [、]区切りの文字列に変換
        materials = "、 ".join(item for item in recipe.get("recipeMaterial", [])) # 材料リスト
        
        # レシピ情報を格納
        recipes_data.append({
            "recipeId": recipe.get("recipeId"), # レシピID
            "recipeTitle": recipe.get("recipeTitle"), # レシピタイトル
            "recipeUrl": recipe.get("recipeUrl"), # レシピURL
            "foodImageUrl": recipe.get("foodImageUrl"), # 食材画像URL
            "recipeCost": recipe.get("recipeCost"), # レシピコスト
            "recipeIndication": recipe.get("recipeIndication"), # レシピ指示
            "recipeMaterial": materials, # 材料リスト
            "categoryId": category_id, # カテゴリID
            "pickup": recipe.get("pickup"), # ピックアップ
            "shop": recipe.get("shop"), # ショップ
            "nickname": recipe.get("nickname"), # ニックネーム
            "rank": recipe.get("rank") # ランク
        })
        
    return recipes_data # レシピ情報を返す
    
def main(): # メイン関数
    """
    楽天レシピの全レシピの人気レシピを取得
    CSVファイルに出力
    """
    # カテゴリリストを取得
    category_df = get_all_categories() # カテゴリ情報を取得
    if category_df.empty: # カテゴリ情報が空の場合
        logging.error("カテゴリデータが取得できませんでした。終了します。")
        return # 終了
    
    # 各カテゴリのレシピを順番に取得
    all_recipes = [] # 全レシピを格納するリスト
    logging.info("全カテゴリのレシピ取得を開始します。")
    # tqdmを使って進捗を目視で表示
    for index, row in tqdm(category_df.iterrows(), total=len(category_df), desc="レシピ取得中"): # 各カテゴリ
        category_id = row["categoryId"] # カテゴリID
        recipes = get_category_recipes(category_id) # 指定されたカテゴリの人気レシピを取得
        if recipes: # レシピが存在する場合
            # 各レシピにカテゴリ名を追加
            for recipe in recipes: # 各レシピ
                recipe["categoryName"] = row["categoryName"] # カテゴリ名
            all_recipes.extend(recipes) # 全レシピに追加
                
        # APIへの負荷軽減のために 3秒待機
        time.sleep(REQUEST_WAIT_TIME)
    
    if not all_recipes: # レシピが存在しない場合
        logging.warning("レシピデータが取得できませんでした。終了します。")
        return # 終了
    
    # 取得したレシピをDataFrameに変換し, CSVファイルに出力
    logging.info(f"合計 {len(all_recipes)} 件のレシピデータを取得しました。CSVファイルに保存します")
    final_df = pd.DataFrame(all_recipes) # DataFrameに変換
    
    # カラムの順番を整理
    ordered_columns = [
        "recipeId", # レシピID
        "recipeTitle", # レシピタイトル
        "rank", # ランク
        "recipeCost", # レシピコスト
        "recipeIndication", # レシピ指示
        "recipeMaterial", # 材料
        "categoryId", # カテゴリID
        "categoryName", # カテゴリ名
        "nickname", # ニックネーム
        "recipeUrl", # レシピURL
        "foodImageUrl", # 食材画像
        "pickup", # ピックアップ
        "shop" 
    ]

    # 存在しないカラムがあってもエラーにならないようにする
    final_df = final_df.reindex(columns=ordered_columns)

    try:
        final_df.to_csv(OUTPUT_CSV_PATH, index=False, encoding="utf-8-sig") # CSVファイルに出力
        logging.info(f"CSVファイル '{OUTPUT_CSV_PATH}' にレシピデータが保存されました。")
    except IOError as e:
        logging.error(f"CSVファイルの保存に失敗しました：{e}")
        
if __name__ == "__main__": # メイン処理
    main() # メイン関数を呼び出す
