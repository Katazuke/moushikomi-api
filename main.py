import requests
from flask import Flask,request,jsonify

app = Flask(__name__)

@app.route('/')
def main():
	# クエリパラメータからapplication_idを取得
	application_id = request.args.get('application_id')

	# application_idが指定されていない場合はエラーを返す
	if not application_id:
		return f"Error: 'application_id' parameter is required.", 400

	# 送信先のURLを構築
	url = f'https://moushikomi-uketsukekun.com/maintenance_company/api/v2/entry_heads/{application_id}'
	#url = f'https://moushikomi-uketsukekun.com/maintenance_company/api/v2/entry_heads/3663121'	
	
	#ヘッダ情報を定義（Authorizationヘッダを含む）
	iapikey = 'Token 5a5030e472a8f92a87e4e093f4161944'
	headers = {'Authorization': iapikey}

	# GETリクエストを送信（ヘッダを含む）
	try:
		res = requests.get(url, headers=headers)
		res.raise_for_status() # レスポンスが失敗した場合は例外を発生させる
	
		appjson = res.json()
		
		target_column = "applicant_moving_reason"
	
		MovinReason__c = None
		for entry_body in appjson.get('entry_bodies',[]):
			if entry_body.get('name')==target_column:
				MovingReason__c = data[entry_body.get('choice')]
				break	# 一致するものが見つかったらループを抜ける


		if MovingReason__c is None:
			return jsonify({"error": "No matching entry found."}), 404
		return jsonify({"MovingReason__c": MovingReason__c}), 200
	
	except requests.exceptions.RequestException as e:
		return jsonify({"error": str(e)}), 500  # リクエストのエラーをキャッチ

	# IPアドレステスト用URL
	#ipurl = 'http://checkip.dyndns.com/'
	#ipres = requests.get(ipurl)
	#print('IPアドレス：',ipres.text)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
