import requests
from flask import Flask,request,jsonify,json,make_response
import logging

app = Flask(__name__)

# Salesforce接続情報
SF_CLIENT_ID = '3MVG96vIeT8jJWjKIhbYEse7lgOxIGPVFHjLMpe1oRUNOYQ2BO8iykQ08UKN9HZ2Z_ikNFsRV.zo.Mze_H948'
SF_CLIENT_SECRET = 'F142768140C5559BD971EA504CB64524AF6AE9B2EFCEFEF710228A724FCAE88A'
SF_USERNAME = 'dev@a-max.jp.0705test'
SF_PASSWORD = 'Fj3zyT4f'
SF_TOKEN_URL = 'https://a-max--0705test.sandbox.my.salesforce.com/services/oauth2/token'

def get_salesforce_token():
	"""Salesforceのアクセストークンを取得"""
	payload = {
		'grant_type': 'password',
		'client_id': SF_CLIENT_ID,
		'client_secret': SF_CLIENT_SECRET,
		'username': SF_USERNAME,
		'password': SF_PASSWORD
		}
	print(payload)
	response = requests.post(SF_TOKEN_URL, data=payload)
	response.raise_for_status()
	return response.json().get('access_token'), response.json().get('instance_url')

@app.route('/')
def main():
	# クエリパラメータからapplication_idとrecord_idを取得
	application_id = request.args.get('application_id')
	record_id = request.args.get('record_id')

	# application_idが指定されていない場合はエラーを返す
	if not application_id:
		return f"Error: 'application_id' parameter is required.", 400
	#if not recor_id:
		#return f"Error: 'record_id' parameter is required.", 400

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
			"EmergencyContact__c": None,
			"EmergencyContactKana__c": None,
			"EmergencyContactSex__c": None,
			"EmergencyContactRelationship__c": None,
			}
		#target_column = "applicant_moving_reason"
		target_columns = [
					['EmergencyContact__c','guarantor_name_kana','last_name'],
					['EmergencyContactKana__c','guarantor_name_kana','"last_name_kana'],
					['EmergencyContactSex__c','applicant_sex','choice'],
					['EmergencyContactRelationship__c','guarantor_relationship','choice"']
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
		# Salesforceのレコード更新
		access_token, instance_url = get_salesforce_token()
		print(access_token)
		print(instance_url)
		sf_url = f"{instance_url}/services/data/v54.0/sobjects/Application__c/{record_id}"  # Replace 'YourObjectName'

		sf_headers = {
			'Authorization': f'Bearer {access_token}',
			'Content-Type': 'application/json'
			}

		sf_response = requests.patch(sf_url, headers=sf_headers, json=variables)
		if sf_response.status_code == 204:
			return jsonify({"success": "Record updated successfully"}), 200
		else:
			error_message = sf_response.json() if sf_response.content else {"error": "Unknown error"}
			logging.error(f"Salesforce API error: {error_message}")
			return jsonify({"error": error_message}), sf_response.status_code


	
	except requests.exceptions.RequestException as e:
		return make_response(json.dumps({"error": str(e)}, ensure_ascii=False)), 500  # リクエストのエラーをキャッチ

	# IPアドレステスト用URL
	#ipurl = 'http://checkip.dyndns.com/'
	#ipres = requests.get(ipurl)
	#print('IPアドレス：',ipres.text)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
