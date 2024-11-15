import requests
from flask import Flask,request,jsonify,json,make_response
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

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

def map_variables(data, columns):
	"""汎用的なマッピング関数"""
	variables = {}
	for key, entry_name, field_name in columns:
		if field_name is None:
			variables[key] = data.get(entry_name)
		else:
			for entry_body in data.get("entry_bodies", []):
				if entry_body.get("name") == entry_name:
					variables[key] = entry_body.get(field_name, "")
					break
	return variables


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
		except ValueError:
			logging.error("Failed to parse JSON from external API response")
			return jsonify({"error": "Invalid JSON response from external API"}), 500
		
		#賃借人オブジェクトのSF変数を定義
		rntvariables ={
			"RenterType__c":None,
			"LastName__c":None,
			"FirstName__c":None,
			"Birthday__c":None,
			}
		
		#申込オブジェクトのSF変数を定義
		appvariables = {
			"EmergencyContact__c": None,
			"EmergencyContactKana__c": None,
			"EmergencyContactSex__c": None,
			"EmergencyContactRelationship__c": None
			}
		
		# 賃借人オブジェクトのマッピング条件
		renter_columns = [
			("RenterType__c", "corp", None),  # 1階層目
			("LastName__c", "applicant_name_kana", "last_name"),  # 2階層目
			("FirstName__c", "applicant_name_kana", "first_name"),  # 2階層目
			("Birthday__c", "applicant_birthday", "birthday"),  # 2階層目
			]

		# 申込オブジェクトのマッピング条件
		app_columns = [
			("EmergencyContact__c", "emergency_name_kana", "last_name"),
			("EmergencyContactKana__c", "emergency_name_kana", "last_name_kana"),
			("EmergencyContactSex__c", "emergency_sex", "choice"),
			("EmergencyContactRelationship__c", "emergency_relationship", "choice"),
			]
	
		# データ取得
		rntvariables = map_variables(appjson, renter_columns)
		appvariables = map_variables(appjson, app_columns)
		
		#アクセストークンを取得してSFAPIのヘッダを構築
		access_token, instance_url = get_salesforce_token()
		sf_headers = {
			'Authorization': f'Bearer {access_token}',
			'Content-Type': 'application/json',
			}

		# 賃借人オブジェクトの更新
		renter_url = f"{instance_url}/services/data/v54.0/sobjects/Renter__c/{record_id}"
		renter_response = requests.patch(renter_url, headers=sf_headers, json=rntvariables)
		if renter_response.status_code != 204:
			error_message = renter_response.json() if renter_response.content else {"error": "Unknown error"}
			logging.error(f"Salesforce Renter update error: {error_message}")
			return jsonify({"error": error_message}), renter_response.status_code

		# 申込オブジェクトの更新
		app_url = f"{instance_url}/services/data/v54.0/sobjects/Application__c/{record_id}"
		app_response = requests.patch(app_url, headers=sf_headers, json=appvariables)
		if app_response.status_code != 204:
			error_message = app_response.json() if app_response.content else {"error": "Unknown error"}
			logging.error(f"Salesforce Application update error: {error_message}")
			return jsonify({"error": error_message}), app_response.status_code

		return jsonify({"success": "Both records updated successfully"}), 200

	except requests.exceptions.RequestException as e:
		logging.error(f"Request error: {e}")
		return jsonify({"error": str(e)}), 500


	# IPアドレステスト用URL
	#ipurl = 'http://checkip.dyndns.com/'
	#ipres = requests.get(ipurl)
	#print('IPアドレス：',ipres.text)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
