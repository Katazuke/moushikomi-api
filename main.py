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

RENTER_COLUMNS_MAPPING = { 						# RenterType による契約者マッピング条件の辞書
	"個人": [
		("RenterType__c",None,None),
		("LastName__c", "applicant_name_kana", "last_name"),	# 2階層目
		("FirstName__c", "applicant_name_kana", "first_name"),	
		("Birthday__c", "applicant_birthday", "birthday"),
		],
	"法人": [
		("RenterType__c",None,None),
		("LastName__c", "corp_applicant_workplace", "text"),  	# 2階層目
		("CorporateNumber__c", "corp_info_corporate_number", "text"),  
		("Birthday__c", "corp_info_foundation_date", "date"),  
		],
	"入居者": [
		("RenterType__c",None,None),
		("LastName__c", "tenant1_name_kana", "last_name"),  	# 2階層目
		("FirstName__c", "tenant1_name_kana", "first_name"),  
		("Birthday__c", "tenant1_birthday","birthday"),  
		],
	}


APPLICATION_COLUMNS_MAPPING = [
		("Contractor__c",None,None),
		("Resident1__c",None,None),
		("EmergencyContact__c", "emergency_name_kana", "last_name"),
		("EmergencyContactKana__c", "emergency_name_kana", "last_name_kana"),
		("EmergencyContactSex__c", "emergency_sex", "choice"),
		("EmergencyContactRelationship__c", "emergency_relationship", "choice"),
		]

def get_salesforce_token():
	"""Salesforceのアクセストークンを取得"""
	payload = {
		'grant_type': 'password',
		'client_id': SF_CLIENT_ID,
		'client_secret': SF_CLIENT_SECRET,
		'username': SF_USERNAME,
		'password': SF_PASSWORD
		}
	response = requests.post(SF_TOKEN_URL, data=payload)
	response.raise_for_status()
	return response.json().get('access_token'), response.json().get('instance_url')


def map_variables(data, columns):
	"""汎用的なマッピング関数"""
	variables = {}
	for key, entry_name, field_name in columns:
		if entry_name is None:
			variables[key] = None
		elif field_name is None:
			variables[key] = data.get(entry_name)
		else:
			for entry_body in data.get("entry_bodies", []):
				if entry_body.get("name") == entry_name:
					variables[key] = entry_body.get(field_name, "")
					break
	return variables

def check_duplicate_record(instance_url, headers, renter_data):
	"""賃借人オブジェクト内の重複チェック"""
	if renter_data["RenterType__c"] == "法人":
		query = f"SELECT Id FROM Renter__c WHERE CorporateNumber__c = '{renter_data.get('CorporateNumber__c')}'"
	else:
		query = (
			f"SELECT Id FROM Renter__c WHERE LastName__c = '{renter_data.get('LastName__c')}' "
			f"AND FirstName__c = '{renter_data.get('FirstName__c')}' "
			f"AND Birthday__c = '{renter_data.get('Birthday__c')}'"
		)
	url = f"{instance_url}/services/data/v54.0/query?q={query}"
	response = requests.get(url, headers=headers)
	response.raise_for_status()
	records = response.json().get("records", [])
	return records[0]["Id"] if records else None


def format_birthday(birthday):
	"""Birthday__c を YYYY-MM-DD の形式に変換"""
	try: # ISO 8601形式をパースして YYYY-MM-DD形式にフォーマット
		date_obj = datetime.fromisoformat(birthday.split(".")[0])  # ミリ秒とタイムゾーンを無視
		return date_obj.strftime("%Y-%m-%d")
	except ValueError:
		logging.error(f"Invalid birthday format: {birthday}")
		return None


def create_renter_record(instance_url, headers, renter_data):
	"""新しい Renter__c レコードを作成し、その ID を返す"""
	url = f"{instance_url}/services/data/v54.0/sobjects/Renter__c"
	try:
		response = requests.post(url, headers=headers, json=renter_data)
		response.raise_for_status()  # エラーチェック
		created_record = response.json()  # 作成されたレコードのレスポンスを取得
		logging.info(f"Record created successfully: {created_record}")
		return created_record  # 作成されたレコードの詳細を返す
	except requests.exceptions.HTTPError as e:
		logging.error(f"HTTP Error: {e}")
		logging.error(f"Response content: {response.text}")
		raise  # エラーを呼び出し元に伝える

def map_relationship(value):
	"""指定された関係性データをSalesforce選択肢に変換"""
	relationship_mapping = {
		"父母": "親",
		"祖父母": "その他",
		"子": "子",
		"孫": "その他",
		"兄弟姉妹": "兄弟姉妹",
		"配偶者": "配偶者",
		"その他": "その他"
		}
	# マッピングが存在しない場合はデフォルトで 'その他' を返す
	return relationship_mapping.get(value, "その他")


@app.route('/')
def main():
	# STEP 1: クエリパラメータからapplication_idとrecord_idを取得
	application_id = request.args.get('application_id')
	record_id = request.args.get('record_id')

	# application_idが指定されていない場合はエラーを返す
	if not application_id:
		return jsonify({"error": "'application_id' parameter is required."}), 400
	#if not recor_id:
		#return f"Error: 'record_id' parameter is required.", 400

	# STEP 2: APIからデータ取得
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
		
	
	# STEP 3: 個人/法人のマッピング表を選択
	# 賃借人オブジェクトから個人/法人に分けて契約者のマッピング表を選択
	renter_type = "法人" if appjson.get("corp") else "個人"
	renter_data =  map_variables(appjson, RENTER_COLUMNS_MAPPING[renter_type])
	renter_data["RenterType__c"] = renter_type
	renter_data["Birthday__c"] = format_birthday(renter_data["Birthday__c"])

	# 賃借人オブジェクトから個人/法人に分けて入居者のマッピング表を選択
	tenant_data =  map_variables(appjson, RENTER_COLUMNS_MAPPING["入居者"])
	tenant_data["RenterType__c"] = "個人"
	tenant_data["Birthday__c"] = format_birthday(tenant_data["Birthday__c"])

	# STEP 4: 契約者情報の重複チェック
	#アクセストークンを取得してSFAPIのヘッダを構築
	access_token, instance_url = get_salesforce_token()
	sf_headers = {
		'Authorization': f'Bearer {access_token}',
		'Content-Type': 'application/json',
	}

	# 契約者重複チェックと重複しない場合に新規作成
	duplicate_id = check_duplicate_record(instance_url, headers, renter_data)
	if duplicate_id: # 重複があった場合、既存のRenter__cレコードIDを一時変数に格納
		contractor_id = duplicate_id
	else:            # 重複がない場合、新しい Renter__c レコードを作成
		logging.info(f"renter_data: {renter_data}")
		new_record = create_renter_record(instance_url, sf_headers, renter_data)
		contractor_id = new_record.get("id")
	
	# 入居者重複チェックと重複しない場合に新規作成
	duplicate_id = check_duplicate_record(instance_url, headers, tenant_data)
	if duplicate_id:
		tenant_id = duplicate_id
	else:		# 重複がない場合、新しい Renter__c レコードを作成
		logging.info(f"tenant_data: {renter_data}")
		new_record = create_renter_record(instance_url, sf_headers, tenant_data)
		tenant_id = new_record.get("id")


	# STEP 7: 申込情報の更新	
	# データ取得
	app_data = map_variables(appjson, APPLICATION_COLUMNS_MAPPING)
	

	# Relationship の選択肢を変換
	if "EmergencyContactRelationship__c" in app_data:
		app_data["EmergencyContactRelationship__c"] = map_relationship(app_data["EmergencyContactRelationship__c"])

	#契約者と入居者レコードIDを埋める
		app_data[Contractor__C]=contractor_id
		app_data[Resident__C]=tenant_id


	# 申込オブジェクトの更新
	app_url = f"{instance_url}/services/data/v54.0/sobjects/Application__c/{record_id}"
	app_response = requests.patch(app_url, headers=sf_headers, json=app_data)
	if app_response.status_code != 204:
		error_message = app_response.json() if app_response.content else {"error": "Unknown error"}
		logging.error(f"Salesforce Application update error: {error_message}")
		return jsonify({"error": error_message}), app_response.status_code

	return jsonify({"success": "Data processed successfully"}), 200
	

	# IPアドレステスト用URL
	#ipurl = 'http://checkip.dyndns.com/'
	#ipres = requests.get(ipurl)
	#print('IPアドレス：',ipres.text)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
