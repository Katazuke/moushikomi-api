import requests
from flask import Flask

app = Flask(__name__)

@app.route('/')
def main():
	# 送信先のURL
	url = 'https://moushikomi-uketsukekun.com/maintenance_company/api/content_images/19086285'

	#ヘッダ情報を定義（Authorizationヘッダを含む）
	headers = {
    	'Authorization': 'Token 5a5030e472a8f92a87e4e093f4161944',
	}

	# GETリクエストを送信（ヘッダを含む）
	res = requests.get(url, headers=headers)

	# ステータスコードの表示
	print('ステータスコード:', response.status_code)

	# レスポンス内容の表示（テキスト形式）
	print('レスポンス本文:', response.text)

	return

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
