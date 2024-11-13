import requests
from flask import Flask,request,jsonify,json,make_response

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
		print(appjson)
		
		#target_column = "applicant_moving_reason"
		target_columns = [
					['LastName__c','applicant_name_kana','last_name'],
					['FirstName__c','applicant_name_kana','first_name'],
					['Sex__c','applicant_sex','"choice"'],
					['Birthday__c','applicant_birthday','"birthday']
				]
	
		for i in range(len(target_columns)):  # i を 0 から 3 まで繰り返す
			for entry_body in appjson.get('entry_bodies', []):
				# target_columns[i][1] が entry_body['name'] に一致するかチェック
				if entry_body.get('name') == target_columns[i][1]:
					# 一致する場合、対応する値を取得して target_columns[i][0] に格納
					target_columns[i][0] = entry_body.get(target_columns[i][2], '')
					print(target_columns[i][0])
					break  # 一致するものが見つかったら内側のループを抜ける
		

		if target_columns[1][0] is None:
			return make_response(json.dumps({"error": "No matching entry found."}, ensure_ascii=False)), 404
		# カスタムレスポンスでエスケープを防ぐ
		print(target_columns[1][0])
		response_data = {"target_columns[1][0]": target_columns[1][0]}
		response = make_response(json.dumps(response_data, ensure_ascii=False))
		response.headers['Content-Type'] = 'application/json; charset=utf-8'
		return response, 200
	
	except requests.exceptions.RequestException as e:
		return make_response(json.dumps({"error": str(e)}, ensure_ascii=False)), 500  # リクエストのエラーをキャッチ

	# IPアドレステスト用URL
	#ipurl = 'http://checkip.dyndns.com/'
	#ipres = requests.get(ipurl)
	#print('IPアドレス：',ipres.text)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
