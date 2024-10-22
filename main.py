import requests
from flask import Flask

app = Flask(__name__)

@app.route('/')
def main():
	# 送信先のURL
	#url = 'http://checkip.dyndns.com/'
	url = 'https://moushikomi-uketsukekun.com/maintenance_company/api/v2/entry_heads/3637058'
	iapikey = 'Token 5a5030e472a8f92a87e4e093f4161944'
	
	#ヘッダ情報を定義（Authorizationヘッダを含む）
	headers = {'Authorization': iapikey}

	# GETリクエストを送信（ヘッダを含む）
	res = requests.get(url, headers=headers)
	#res = requests.get(url)

	# ステータスコードの表示
	print('ステータスコード:', res.status_code)
	
	# エラーハンドリング
	if res.status_code != 200:
		return f"Error: {res.status_code} - {res.text}",
		res.status_code

	# レスポンス内容の表示（JSON形式）
	print('レスポ本文:', res.json())  # JSON形式での表示

	return res.text  #レスポンスを返す

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
