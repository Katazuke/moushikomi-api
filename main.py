import requests
from flask import Flask,request,jsonify,json,make_response
import logging
from datetime import datetime

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

def format_birthday(birthday):
	"""Birthday__c を YYYY-MM-DD の形式に変換"""
	try: # ISO 8601形式をパースして YYYY-MM-DD形式にフォーマット
		date_obj = datetime.fromisoformat(birthday.split(".")[0])  # ミリ秒とタイムゾーンを無視
		return date_obj.strftime("%Y-%m-%d")
	except ValueError:
		logging.error(f"Invalid birthday format: {birthday}")
		return None

def get_duplicate_record_id(instance_url, headers, last_name, first_name, birthday):
	"""Salesforceで重複レコードを検索し、IDを取得"""
	query = (
		f"SELECT Id FROM Renter__c WHERE LastName__c = '{last_name}' "
		f"AND FirstName__c = '{first_name}' AND Birthday__c ={birthday}"
		)
		
	url = f"{instance_url}/services/data/v54.0/query?q={query}"
	response = requests.get(url, headers=headers)
	response.raise_for_status()
	records = response.json().get("records", [])
	print(records)
	return records[0]["Id"] if records else None


def create_renter_record(instance_url, headers, renter_data):
	"""新しい Renter__c レコードを作成"""
	url = f"{instance_url}/services/data/v54.0/sobjects/Renter__c"
	response = requests.post(url, headers=headers, json=renter_data)
	response.raise_for_status()
	return response.json()

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
	
	#ヘッダ情報を定義（Authorizationヘッダを含む）
	iapikey = 'Token 5a5030e472a8f92a87e4e093f4161944'
	headers = {'Authorization': iapikey}

	# GETリクエストを送信（ヘッダを含む）
	try:
		#申込受付くんからJSON文を取得
		res = requests.get(url, headers=headers)
		res.raise_for_status() # レスポンスが失敗した場合は例外を発生させる
		appjson = res.json()
		
		#申込受付くんAPIエラーハンドリング
	except ValueError:
		logging.error("Failed to parse JSON from external API response")
		return jsonify({"error": "Invalid JSON response from external API"}), 500
		
		
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
		
	# Birthday__c を yyyymmdd にフォーマット
	formatted_birthday = format_birthday(rntvariables.get("Birthday__c"))
	if not formatted_birthday:
		return jsonify({"error": "Invalid Birthday__c format"}), 400
	rntvariables["Birthday__c"] = formatted_birthday

	#アクセストークンを取得してSFAPIのヘッダを構築
	access_token, instance_url = get_salesforce_token()
	sf_headers = {
		'Authorization': f'Bearer {access_token}',
		'Content-Type': 'application/json',
	}

	# RenterType__c が False の場合、重複チェックと新規作成
	if not rntvariables.get("RenterType__c"):
		last_name = rntvariables.get("LastName__c")
		first_name = rntvariables.get("FirstName__c")
		birthday = rntvariables.get("Birthday__c")
		duplicate_id = get_duplicate_record_id(instance_url, sf_headers, last_name, first_name, birthday)
	
		
		if duplicate_id: # 重複があった場合、既存のRenter__cレコードIDをappvariablesに格納
			appvariables["Contructor__c"] = duplicate_id
		else:            # 重複がない場合、新しい Renter__c レコードを作成
			renter_data = {
				"LastName__c": last_name,
				"FirstName__c": first_name,
				"Birthday__c": birthday,
			}
		new_record = create_renter_record(instance_url, sf_headers, renter_data)
		appvariables["Contructor__c"] = new_record.get("id")

	# 申込オブジェクトの更新
	app_url = f"{instance_url}/services/data/v54.0/sobjects/Application__c/{record_id}"
	app_response = requests.patch(app_url, headers=sf_headers, json=appvariables)
	if app_response.status_code != 204:
		error_message = app_response.json() if app_response.content else {"error": "Unknown error"}
		logging.error(f"Salesforce Application update error: {error_message}")
		return jsonify({"error": error_message}), app_response.status_code

	return None
	

	# IPアドレステスト用URL
	#ipurl = 'http://checkip.dyndns.com/'
	#ipres = requests.get(ipurl)
	#print('IPアドレス：',ipres.text)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
