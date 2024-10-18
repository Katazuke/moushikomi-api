import requests

# 送信先のURL
url = 'https://example.com'

# GETリクエストを送信
response = requests.get(url)

# ステータスコードの表示
print('ステータスコード:', response.status_code)

# レスポンス内容の表示（テキスト形式）
print('レスポンス本文:', response.text)