=====

楽天レシピAPIでカテゴリリストと人気ランキングを取得するヤツ  

[ 制作環境 ]  
Python 3.13.0  
Gemini Code Assist  
VSCode  

[ 参考サイト ]  
https://qiita.com/run1000dori/items/7ffa7907a6c03c8909fc  
https://qiita.com/anzuuuuu/items/be4e4845c21ac3334695  
https://webservice.rakuten.co.jp/documentation/recipe-category-list  

[ 同梱 ]  
rakuten_recipe.py (本体)の他  
- sql_excel_csv.py  
    CSVをデータベースにエクスポートする  
- db_url_web.py  
    (データベースから)レシピIDを入力すると, ブラウザが開きレシピを確認できるGUI    

[ How to use ]  
・本体 ( rakuten_recipe.py ) を実行する  
- APIを使って, 全カテゴリからと人気ランキング上位4位までのレシピを取得する  
- ダウンロードしたリストは, CSVファイルとして保存される  

[ ⚠️ 注意事項 ]  
- APIに負荷をかけないよう, リクエスト間隔に余裕を持たせること  
- リストのダウンロードには, かなりの時間を要するため  
    PCのスペックに余裕があれば, 他のタスクをこなすことをお勧めする   
    (目安: 2164件のリストを3秒間隔でダウンロードすると, 約2時間)  
- CSVをデータベース化して扱ったほうが便利かもしれない…  
    ex: ローカルで使える SQLite3, A5M2 など  
        VSCode拡張機能であるSQLite, SQLite Viewer など  

=====
