import requests
from flask import Flask,request,json

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
	# IPアドレステスト用URL
	#ipurl = 'http://checkip.dyndns.com/'
	
	
	#ヘッダ情報を定義（Authorizationヘッダを含む）
	iapikey = 'Token 5a5030e472a8f92a87e4e093f4161944'
	headers = {'Authorization': iapikey}

	# GETリクエストを送信（ヘッダを含む）
	res = requests.get(url, headers=headers)
	#ipres = requests.get(ipurl)

	appjson = json.loads(res.text)

	target_column = "applicant_moving_reason"
	indices = []


	for i, entry_body in enumerate(appjson['entry_bodies']):
		if entry_bodies['name']==target_column:
			if entry_body is not None and entry_body.get('name') == target_column:
				indices.append(i)
				MovingReason__c = appjson['entry_bodies'][indices.append(i)][choice]



	# ステータスコードの表示
	print('ステータスコード:', res.status_code)
	
	# エラーハンドリング
	#if res.status_code != 200:
	#	return f"Error: {res.status_code} - {res.text}", res.status_code
	# レスポンス内容の表示（JSON形式）
	#print('IPアドレス：',ipres.text)
	print('転居理由：',MovingReason__c)

	 # 結果をJSON形式で返す
	return MovingReason__c

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
