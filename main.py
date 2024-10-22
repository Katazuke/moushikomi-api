import requests
from flask import Flask

app = Flask(__name__)

@app.route('/')
def main():
	# 送信先のURL
	url = 'http://checkip.dyndns.com/'
	iapikey = 'Token 5a5030e472a8f92a87e4e093f4161944'
	
	#ヘッダ情報を定義（Authorizationヘッダを含む）
	headers = {'Authorization': iapikey}

	# GETリクエストを送信（ヘッダを含む）
	res = requests.get(url, headers=headers)
	#res = requests.get(url)

	# ステータスコードの表示
	print('ステータスコード:', res.status_code)

	# レスポンス内容の表示（テキスト形式）
	print('レスポンス本文:', res.text)

	return res.text  #レスポンスを返す

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
