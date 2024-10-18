import requests

# 送信先のURL
url = 'https://moushikomi-uketsukekun.com/maintenance_company/api/v2/entry_heads/3637058'

# GETリクエストを送信
response = requests.get(url)

# ステータスコードの表示
print('ステータスコード:', response.status_code)

# レスポンス内容の表示（テキスト形式）
print('レスポンス本文:', response.text)