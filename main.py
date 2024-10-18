import requests

# 送信先のURL
url = 'https://moushikomi-uketsukekun.com/maintenance_company/api/v2/entry_heads/3637058'

# ヘッダ情報を定義（Authorizationヘッダを含む）
headers = {
    'Authorization': 'Token 5a5030e472a8f92a87e4e093f4161944',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

# GETリクエストを送信（ヘッダを含む）
response = requests.get(url, headers=headers)

# ステータスコードの表示
print('ステータスコード:', response.status_code)

# レスポンス内容の表示（テキスト形式）
print('レスポンス本文:', response.text)文:', response.text)