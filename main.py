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
		
		variables = {
			"LastName__c": None,
			"FirstName__c": None,
			"Sex__c": None,
			"Birthday__c": None,
			}
		#target_column = "applicant_moving_reason"
		target_columns = [
					['LastName__c','applicant_name_kana','last_name'],
					['FirstName__c','applicant_name_kana','first_name'],
					['Sex__c','applicant_sex','"choice"'],
					['Birthday__c','applicant_birthday','"birthday']
				]
	
		# 各エントリを処理して値を辞書に格納
		for column in target_columns:
			key, entry_name, field_name = column  # 要素を展開

			for entry_body in appjson.get('entry_bodies', []):
				if entry_body.get('name') == entry_name:
					# 辞書内の該当キーに値を格納
					variables[key] = entry_body.get(field_name, '')
					break  # 一致するものが見つかったら内側のループを抜ける	
		if all(value is None for value in variables.values()):
			return make_response(json.dumps({"error": "No matching entry found."}, ensure_ascii=False)), 404
		# カスタムレスポンスでエスケープを防ぐ
		
		print(variables)
		response_data = {"variables": variables}
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
