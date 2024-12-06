import requests
from flask import Flask,request,jsonify,json,make_response,redirect, url_for
import logging
from datetime import datetime
import re


app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Salesforce sandbox接続情報
#SF_CLIENT_ID = '3MVG96vIeT8jJWjKIhbYEse7lgOxIGPVFHjLMpe1oRUNOYQ2BO8iykQ08UKN9HZ2Z_ikNFsRV.zo.Mze_H948'
#SF_CLIENT_SECRET = 'F142768140C5559BD971EA504CB64524AF6AE9B2EFCEFEF710228A724FCAE88A'
#SF_USERNAME = 'dev@a-max.jp.0705test'
#SF_PASSWORD = 'Fj3zyT4f
'
#SF_TOKEN_URL = 'https://a-max--0705test.sandbox.my.salesforce.com/services/oauth2/token'

# Salesforce 本番接続情報
SF_CLIENT_ID = '3MVG95wP8n0_BKi2wGVZKeOKujjlv5HCsywGpTnAgKudwE3m6XIhNBXKGdgiqeGVR4RnG7pUGcPPze7a4_M.V'
SF_CLIENT_SECRET = '71214916328D9A54B45B6CCEE0D1C574ADFD1E2992239CA024FDD89F4F3D1EAF'
SF_USERNAME = 'dev@a-max.jp'
SF_PASSWORD = 'Fj3zyT4fu5eieRCRPP0g95Kn8x9d09bB'
SF_TOKEN_URL = 'https://login.salesforce.com/services/oauth2/token'



# ITANDI 接続情報
ITANDI_TOKEN = 'Token 5a5030e472a8f92a87e4e093f4161944'


RENTER_COLUMNS_MAPPING = { 						# RenterType による契約者マッピング条件の辞書
	"個人": {
		"契約者":[
			("RenterType__c",None,None),
			("LastName__c", "applicant_name_kana", "last_name"),	# 2階層目
			("FirstName__c", "applicant_name_kana", "first_name"),	
			("LastNameKana__c","applicant_name_kana","last_name_kana"),
			("FirstNameKana__c","applicant_name_kana","first_name_kana"),
			("Sex__c","applicant_sex","choice"),
			("Nationality__c","applicant_nationality","text"),
			("Birthday__c", "applicant_birthday", "birthday"),
			("MobilePhoneNumber__c","applicant_mobile_tel","phone_number"),
			("PhoneNumber__c","applicant_home_tel","phone_number"),
			("Email__c","applicant_mail","text"),
			("PostCode__c","applicant_address","zip_code"),
			("Prefecture__c","applicant_address","state"),
			("Address1__c","applicant_address","city"),
			("Address2__c","applicant_address","street"),
			("AddressBuilding__c","applicant_address","other"),
			("Company__c","applicant_workplace","text"),
			("CompanyKana__c","applicant_workplace","text_kana"),
			("CompanyPhone__c","applicant_workplace_tel","phone_number"),
			("CompanyAddress_PostalCode__c","applicant_workplace_address","zip_code"),
			("CompanyAddress_State__c","applicant_workplace_address","state"),
			("CompanyAddress_City__c","applicant_workplace_address","city"),
			("CompanyAddress_Street__c","applicant_workplace_address","street"),
			("CompanyAddress_Building__c","applicant_workplace_address","other"),
			("CompanyCapital__c","applicant_workplace_capital","number"),
			("AnnualIncome__c","applicant_workplace_tax_included_annual_income","number"),
			],
		"入居者1":[
			("RenterType__c",None,None),
			("LastName__c", "tenant1_name_kana", "last_name"),  	# 2階層目
			("FirstName__c", "tenant1_name_kana", "first_name"),  
			("Birthday__c", "tenant1_birthday","birthday"), 
			("LastNameKana__c","tenant1_name_kana","last_name_kana"),
			("FirstNameKana__c","tenant1_name_kana","first_name_kana"),
			("Sex__c","tenant1_sex","choice"),
			("MobilePhoneNumber__c","tenant1_mobile_tel","phone_number"),
			("PhoneNumber__c","tenant1_home_tel","phone_number"),
			("Email__c","tenant1_mail","text"),
			("Company__c","tenant1_workplace","text"),
			("CompanyKana__c","tenant1_workplace","text_kana"),
			("AnnualIncome__c","tenant1_workplace_tax_included_annual_income","number"),
			],
		"入居者2":[
			("RenterType__c",None,None),
			("LastName__c", "tenant2_name_kana", "last_name"),  	# 2階層目
			("FirstName__c", "tenant2_name_kana", "first_name"),  
			("Birthday__c", "tenant2_birthday","birthday"), 
			("LastNameKana__c","tenant2_name_kana","last_name_kana"),
			("FirstNameKana__c","tenant2_name_kana","first_name_kana"),
			("Sex__c","tenant2_sex","choice"),
			("MobilePhoneNumber__c","tenant2_mobile_tel","phone_number"),
			("PhoneNumber__c","tenant2_home_tel","phone_number"),
			("Email__c","tenant2_mail","text"),
			("Company__c","tenant2_workplace","text"),
			("CompanyKana__c","tenant2_workplace","text_kana"),
			("AnnualIncome__c","tenant2_workplace_tax_included_annual_income","number"),
			],
		"入居者3":[
			("RenterType__c",None,None),
			("LastName__c", "tenant3_name_kana", "last_name"),  	# 3階層目
			("FirstName__c", "tenant3_name_kana", "first_name"),  
			("Birthday__c", "tenant3_birthday","birthday"), 
			("LastNameKana__c","tenant3_name_kana","last_name_kana"),
			("FirstNameKana__c","tenant3_name_kana","first_name_kana"),
			("Sex__c","tenant3_sex","choice"),
			("MobilePhoneNumber__c","tenant3_mobile_tel","phone_number"),
			("PhoneNumber__c","tenant3_home_tel","phone_number"),
			("Email__c","tenant3_mail","text"),
			("Company__c","tenant3_workplace","text"),
			("CompanyKana__c","tenant3_workplace","text_kana"),
			("AnnualIncome__c","tenant3_workplace_tax_included_annual_income","number"),
			],
		"入居者4":[
			("RenterType__c",None,None),
			("LastName__c", "tenant4_name_kana", "last_name"),  	# 4階層目
			("FirstName__c", "tenant4_name_kana", "first_name"),  
			("Birthday__c", "tenant4_birthday","birthday"), 
			("LastNameKana__c","tenant4_name_kana","last_name_kana"),
			("FirstNameKana__c","tenant4_name_kana","first_name_kana"),
			("Sex__c","tenant4_sex","choice"),
			("MobilePhoneNumber__c","tenant4_mobile_tel","phone_number"),
			("PhoneNumber__c","tenant4_home_tel","phone_number"),
			("Email__c","tenant4_mail","text"),
			("Company__c","tenant4_workplace","text"),
			("CompanyKana__c","tenant4_workplace","text_kana"),
			("AnnualIncome__c","tenant4_workplace_tax_included_annual_income","number"),
			],
		"入居者5":[
			("RenterType__c",None,None),
			("LastName__c", "tenant5_name_kana", "last_name"),  	# 5階層目
			("FirstName__c", "tenant5_name_kana", "first_name"),  
			("Birthday__c", "tenant5_birthday","birthday"), 
			("LastNameKana__c","tenant5_name_kana","last_name_kana"),
			("FirstNameKana__c","tenant5_name_kana","first_name_kana"),
			("Sex__c","tenant5_sex","choice"),
			("MobilePhoneNumber__c","tenant5_mobile_tel","phone_number"),
			("PhoneNumber__c","tenant5_home_tel","phone_number"),
			("Email__c","tenant5_mail","text"),
			("Company__c","tenant5_workplace","text"),
			("CompanyKana__c","tenant5_workplace","text_kana"),
			("AnnualIncome__c","tenant5_workplace_tax_included_annual_income","number"),
			],
		},
	"法人": {
		"契約者":[
			("LastName__c","corp_applicant_workplace","text"),
			("LastNameKana__c","corp_applicant_workplace","text_kana"),
			("CorporateNumber__c","corp_info_corporate_number","text"),
			("PostCode__c","corp_info_head_office_address","zip_code"),
			("Prefecture__c","corp_info_head_office_address","state"),
			("Address1__c","corp_info_head_office_address","city"),
			("Address2__c","corp_info_head_office_address","street"),
			("Address2__c","corp_info_head_office_address","other"),
			("PhoneNumber__c","corp_info_head_office_tel","phone_number"),
			("CompanyCapital__c","corp_info_capital","number"),
			("CompanyCeoLastName__c","corp_ceo_name","last_name"),
			("CompanyCeoFirstName__c","corp_ceo_name","first_name"),
			("CompanyCeoLastNameKana__c","corp_ceo_name","last_name_kana"),
			("CompanyCeoFirstNameKana__c","corp_ceo_name","first_name_kana"),
			("CompanyContactLastName__c","corp_applicant_contact_name","last_name"),
			("CompanyContactFirstName__c","corp_applicant_contact_name","first_name"),
			("CompanyContactLastNameKana__c","corp_applicant_contact_name","last_name_kana"),
			("CompanyContactFirstNameKana__c","corp_applicant_contact_name","first_name_kana"),
			("CompanyContactTel__c","corp_applicant_contact_tel","phone_number"),
			("CompanyContactFax__c","corp_applicant_contact_office_fax","phone_number"),
			("CompanyContactMail__c","corp_applicant_contact_mail","text"),
			("Note__c","corp_applicant_contact_department_name","text"), 
			],
		"入居者1": [
			("RenterType__c",None,None),
			("LastName__c","corp_tenant1_name_kana","last_name"),
			("FirstName__c","corp_tenant1_name_kana","first_name"),
			("LastNameKana__c","corp_tenant1_name_kana","last_name_kana"),
			("FirstNameKana__c","corp_tenant1_name_kana","first_name_kana"),
			("Sex__c","corp_tenant1_sex","choice"),
			("Nationality__c","corp_tenant1_nationality","text"),
			("Birthday__c","corp_tenant1_birthday","birthday"),
			("MobilePhoneNumber__c","corp_tenant1_mobile_tel","phone_number"),
			("PhoneNumber__c","corp_tenant1_home_tel","phone_number"),
			("Email__c","corp_tenant1_mail","text"),
			("Company__c","corp_tenant1_workplace","text"),
			("CompanyKana__c","corp_tenant1_workplace","text_kana"),
			("CompanyPhone__c","corp_tenant1_workplace_tel","phone_number"),
			("CompanyAddress_PostalCode__c","corp_tenant1_address","zip_code"),
			("CompanyAddress_State__c","corp_tenant1_address","state"),
			("CompanyAddress_City__c","corp_tenant1_address","city"),
			("CompanyAddress_Street__c","corp_tenant1_address","street"),
			("CompanyAddress_Building__c","corp_tenant1_address","other"),
			("AnnualIncome__c","corp_tenant1_workplace_tax_included_annual_income","number"),
	  		],
		"入居者2": [
			("RenterType__c",None,None),
			("LastName__c","corp_tenant2_name_kana","last_name"),
			("FirstName__c","corp_tenant2_name_kana","first_name"),
			("LastNameKana__c","corp_tenant2_name_kana","last_name_kana"),
			("FirstNameKana__c","corp_tenant2_name_kana","first_name_kana"),
			("Sex__c","corp_tenant2_sex","choice"),
			("Nationality__c","corp_tenant2_nationality","text"),
			("Birthday__c","corp_tenant2_birthday","birthday"),
			("MobilePhoneNumber__c","corp_tenant2_mobile_tel","phone_number"),
			("PhoneNumber__c","corp_tenant2_home_tel","phone_number"),
			("Email__c","corp_tenant2_mail","text"),
			("Company__c","corp_tenant2_workplace","text"),
			("CompanyKana__c","corp_tenant2_workplace","text_kana"),
			("CompanyPhone__c","corp_tenant2_workplace_tel","phone_number"),
			("AnnualIncome__c","corp_tenant2_workplace_tax_included_annual_income","number"),
	  		],
		"入居者3": [
			("RenterType__c",None,None),
			("LastName__c","corp_tenant3_name_kana","last_name"),
			("FirstName__c","corp_tenant3_name_kana","first_name"),
			("LastNameKana__c","corp_tenant3_name_kana","last_name_kana"),
			("FirstNameKana__c","corp_tenant3_name_kana","first_name_kana"),
			("Sex__c","corp_tenant3_sex","choice"),
			("Nationality__c","corp_tenant3_nationality","text"),
			("Birthday__c","corp_tenant3_birthday","birthday"),
			("MobilePhoneNumber__c","corp_tenant3_mobile_tel","phone_number"),
			("PhoneNumber__c","corp_tenant3_home_tel","phone_number"),
			("Email__c","corp_tenant3_mail","text"),
			("Company__c","corp_tenant3_workplace","text"),
			("CompanyKana__c","corp_tenant3_workplace","text_kana"),
			("CompanyPhone__c","corp_tenant3_workplace_tel","phone_number"),
			("AnnualIncome__c","corp_tenant3_workplace_tax_included_annual_income","number"),
	  		],
		"入居者4": [
			("RenterType__c",None,None),
			("LastName__c","corp_tenant4_name_kana","last_name"),
			("FirstName__c","corp_tenant4_name_kana","first_name"),
			("LastNameKana__c","corp_tenant4_name_kana","last_name_kana"),
			("FirstNameKana__c","corp_tenant4_name_kana","first_name_kana"),
			("Sex__c","corp_tenant4_sex","choice"),
			("Nationality__c","corp_tenant4_nationality","text"),
			("Birthday__c","corp_tenant4_birthday","birthday"),
			("MobilePhoneNumber__c","corp_tenant4_mobile_tel","phone_number"),
			("PhoneNumber__c","corp_tenant4_home_tel","phone_number"),
			("Email__c","corp_tenant4_mail","text"),
			("Company__c","corp_tenant4_workplace","text"),
			("CompanyKana__c","corp_tenant4_workplace","text_kana"),
			("CompanyPhone__c","corp_tenant4_workplace_tel","phone_number"),
			("AnnualIncome__c","corp_tenant4_workplace_tax_included_annual_income","number"),
	  		],
		"入居者5": [
			("RenterType__c",None,None),
			("LastName__c","corp_tenant5_name_kana","last_name"),
			("FirstName__c","corp_tenant5_name_kana","first_name"),
			("LastNameKana__c","corp_tenant5_name_kana","last_name_kana"),
			("FirstNameKana__c","corp_tenant5_name_kana","first_name_kana"),
			("Sex__c","corp_tenant5_sex","choice"),
			("Nationality__c","corp_tenant5_nationality","text"),
			("Birthday__c","corp_tenant5_birthday","birthday"),
			("MobilePhoneNumber__c","corp_tenant5_mobile_tel","phone_number"),
			("PhoneNumber__c","corp_tenant5_home_tel","phone_number"),
			("Email__c","corp_tenant5_mail","text"),
			("Company__c","corp_tenant5_workplace","text"),
			("CompanyKana__c","corp_tenant5_workplace","text_kana"),
			("CompanyPhone__c","corp_tenant5_workplace_tel","phone_number"),
			("AnnualIncome__c","corp_tenant5_workplace_tax_included_annual_income","number"),
	  		],
		},
	}

APPLICATION_COLUMNS_MAPPING = [
		("Contractor__c",None,None),
		("Resident1__c",None,None),
		("IndividualCorporation__c",None,None),
		("EmergencyContactSex__c", "emergency_sex", "choice"),
		("EmergencyContactRelationship__c", "emergency_relationship", "choice"),
		("EmergencyContactRelationship__c", "corp_emergency_relationship", "choice"),
		("LeasingId__c","room_key",None),
		("ExternalStatusID__c","entry_status_id",None),
		("ApplicationDate__c","created_at",None),
		("ExternalUpdatedDate__c","updated_at",None),
		("ApplyCount__c","priotity",None),
		("Pet__c","is_pet","choice"),
		("PetCount__c","number_of_pets","number"),
		("PetType__c","pet_classification","choice"),
		("PetType__c","pet_type","text"),
		("PetType__c","pet_size","choice"),
		("PetType__c","pet_details","text"),
		("InstrumentUse__c","is_instrument","choice"),
		("InstrumentType__c","instrument_type","text"),
		("MovingReason__c","applicant_moving_reason","choice"),
		("MovingReason__c","corp_applicant_moving_reason","choice"),
		("Nationality__c","telnet_detail","choice"),
		("Nationality__c","corp_telnet_detail","choice"),
		("ResidentRelationship1__c","tenant1_relationship","choice"),
		("ResidentRelationship2__c","tenant2_relationship","choice"),
		("ResidentRelationship3__c","tenant3_relationship","choice"),
		("ResidentRelationship4__c","tenant4_relationship","choice"),
		("ResidentRelationship5__c","tenant5_relationship","choice"),		
		("ResidentRelationship1__c","corp_tenant1_relationship","choice"),
		("ResidentRelationship2__c","corp_tenant2_relationship","choice"),
		("ResidentRelationship3__c","corp_tenant3_relationship","choice"),
		("ResidentRelationship4__c","corp_tenant4_relationship","choice"),
		("ResidentRelationship5__c","corp_tenant5_relationship","choice"),
		("EmergencyContact__c","emergency_name_kana","last_name"),
		("EmergencyContactKana__c","emergency_name_kana","first_last_kana"),
		("EmergencyContact__c","emergency_name_kana","first_name"),
		("EmergencyContactKana__c","emergency_name_kana","first_name_kana"),
		("EmergencyContact__c","corp_emergency_name_kana","last_name"),
		("EmergencyContactKana__c","corp_emergency_name_kana","first_last_kana"),
		("EmergencyContact__c","corp_emergency_name_kana","first_name"),
		("EmergencyContactKana__c","corp_emergency_name_kana","first_name_kana"),
		("EmergencyContactTel__c","corp_emergency_mobile_tel","phone_number"),
		("EmergencyContactTel__c","corp_emergency_home_tel","phone_number"),
		("EmergencyContactTel__c","emergency_mobile_tel","phone_number"),
		("EmergencyContactTel__c","emergency_home_tel","phone_number"),
		("EmergencyContactAddress_PostalCode__c","emergency_address","zip_code"),
		("EmergencyContactAddress_State__c","emergency_address","state"),
		("EmergencyContactAddress_City__c","emergency_address","city"),
		("EmergencyContactAddress_Street__c","emergency_address","street"),
		("EmergencyContactAddress_Building__c","emergency_address","other"),
		("EmergencyContactAddress_PostalCode__c","corp_emergency_address","zip_code"),
		("EmergencyContactAddress_State__c","corp_emergency_address","state"),
		("EmergencyContactAddress_City__c","corp_emergency_address","city"),
		("EmergencyContactAddress_Street__c","corp_emergency_address","street"),
		("EmergencyContactAddress_Building__c","corp_emergency_address","other"),
		("HousingAgencyContactLastName__c","corp_company_housing_contact_name","last_name"),
		("HousingAgencyContactFirstName__c","corp_company_housing_contact_name","first_name"),
		("HousingAgencyContactLastNameKana__c","corp_company_housing_contact_name","last_name_kana"),
		("HousingAgencyContactFirstNameKana__c","corp_company_housing_contact_name","first_name_kana"),
		("HousingAgencyTell__c","corp_company_housing_tel","phone_number"),
		("HousingAgencyFax__c","corp_company_housing_fax","phone_number"),
		("ResponsiblePerson__c",None,None),
		("ResponsiblePersonPhoneNumber__c",None,None),
		("EResponsiblePersonEmail__c",None,None),
		("BrokerCompany__c",None,None),
		]

#ENTRY_HEAD = [
#		("ExternalId__c","guarantee_plan_id",None),
#		("ExternalCompanyName__c","guarantee","Name"),
#		("PlanName__c","guarantee","plan_name"),
#		("SuretyNumber__c","judgement_result"",result_surety_number),
#		()
#		]

FIELD_TRANSFORMATIONS = {
	"Sex__c": {
		"男": "男性",
		"女": "女性",
		},
	"ResidentRelationship1__c": {
		"父母": "親",
		"祖父母": "その他",
		"子": "子",
		"孫": "その他",
		"兄弟姉妹": "兄弟姉妹",
		"配偶者": "配偶者",
		"その他": "その他",
		"社員": "従業員",
		"社員の配偶者":"入居者親族",
		"社員の子":"入居者親族",
		"社員の親":"入居者親族",
		"社員の祖父母":"入居者親族",
		"社員の孫":"入居者親族",
		"社員の兄弟姉妹":"入居者親族",
		},
	"ResidentRelationship2__c": {
		"父母": "親",
		"祖父母": "その他",
		"子": "子",
		"孫": "その他",
		"兄弟姉妹": "兄弟姉妹",
		"配偶者": "配偶者",
		"その他": "その他",
		"社員": "従業員",
		"社員の配偶者":"入居者親族",
		"社員の子":"入居者親族",
		"社員の親":"入居者親族",
		"社員の祖父母":"入居者親族",
		"社員の孫":"入居者親族",
		"社員の兄弟姉妹":"入居者親族",
		},
	"ResidentRelationship3__c": {
		"父母": "親",
		"祖父母": "その他",
		"子": "子",
		"孫": "その他",
		"兄弟姉妹": "兄弟姉妹",
		"配偶者": "配偶者",
		"その他": "その他",
		"社員": "従業員",
		"社員の配偶者":"入居者親族",
		"社員の子":"入居者親族",
		"社員の親":"入居者親族",
		"社員の祖父母":"入居者親族",
		"社員の孫":"入居者親族",
		"社員の兄弟姉妹":"入居者親族",
		},
	"ResidentRelationship4__c": {
		"父母": "親",
		"祖父母": "その他",
		"子": "子",
		"孫": "その他",
		"兄弟姉妹": "兄弟姉妹",
		"配偶者": "配偶者",
		"その他": "その他",
		"社員": "従業員",
		"社員の配偶者":"入居者親族",
		"社員の子":"入居者親族",
		"社員の親":"入居者親族",
		"社員の祖父母":"入居者親族",
		"社員の孫":"入居者親族",
		"社員の兄弟姉妹":"入居者親族",
		},
	"EmergencyContactRelationship__c": {
		"父母": "親",
		"祖父母": "その他",
		"子": "子",
		"孫": "その他",
		"兄弟姉妹": "兄弟姉妹",
		"配偶者": "配偶者",
		"その他": "その他",
		"社員": "従業員",
		}
	}
	
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

def apply_format(key, value):
	"""汎用的なフォーマット適用関数"""
	if value is None:
		return None

	# フォーマットルールを定義
	format_rules = {
		"postal_code": lambda x: x.replace("-", "").strip() if len(x.replace("-", "").strip()) == 7 and x.replace("-", "").isdigit()else None,
		"date": lambda x: datetime.fromisoformat(x.split(".")[0]).strftime("%Y-%m-%d") if x else None,
		"email": lambda x: x if "@" in x else "no-match@a-max.jp",  # メールアドレスバリデーション
		# 他のフォーマットルールを追加可能
	}

	# キーごとのルールマッピング
	key_format_mapping = {
		"PostCode__c": "postal_code",
		"CompanyAddress_PostalCode__c": "postal_code",
		"Birthday__c": "date",
		"PostCode__c": "postal_code",
		"ApplicationDate__c": "date",
		"ExternalUpdatedDate__c": "data",
		"Email__c": "email",  # メールアドレスフォーマット
		"CompanyContactMail__c": "email",  # メールアドレスフォーマット
	}

	# 適切なフォーマットルールを適用
	rule = key_format_mapping.get(key)
	if rule and rule in format_rules:
		try:
			return format_rules[rule](value)
		except Exception as e:
			logging.error(f"Formatting error for key={key}, value={value}: {e}")
			return None

	# 該当なしの場合はそのまま返す
	return value

def transform_value(key, value):
	"""フィールドごとの変換を適用する汎用関数"""
	if value is None:
		return None
	if key in FIELD_TRANSFORMATIONS:
		# 該当する変換マッピングがあれば適用
		return FIELD_TRANSFORMATIONS[key].get(value, value)
	return value  # 該当しない場合はそのまま返す

# map_variables 関数での利用例
def map_variables(data, columns):
	"""汎用的なマッピング関数。既存の変数値がある場合は全角スペースで値を追加する。"""
	variables = {}
	for key, entry_name, field_name in columns:
		value = None
		if entry_name is None:
			# entry_name が None の場合
			value = None
		elif field_name is None:
			# field_name が None の場合
			value = data.get(entry_name)
		else:
		# entry_bodies 内の特定フィールドを取得
			for entry_body in data.get("entry_bodies", []):
				if entry_body.get("name") == entry_name:
					value = entry_body.get(field_name, "")
					break
		# 改行コードのチェック
		if value and isinstance(value, str) and ('\n' in value or '\r' in value):
			logging.warning(f"Invalid newline characters detected in key={key}, value={value}")
			# 改行コードを削除する場合
			value = value.replace('\n', ' ').replace('\r', ' ')
			# またはエラーをスローする場合
			raise ValueError(f"Newline characters found in value for key={key}: {value}")

		# フォーマット適用
		value = apply_format(key, value)

		# 選択肢変換を適用
		value = transform_value(key, value)

		# 値がすでに変数にあり、新しい値が None でない場合は追加
		if key in variables and variables[key] and value is not None:
			variables[key] += f"　{value}"  # 全角スペースで結合
		elif value is not None:
			variables[key] = value
	return variables

def update_renter_record(instance_url, headers, record_id, renter_data):
	"""既存の Renter__c レコードを更新"""
	url = f"{instance_url}/services/data/v54.0/sobjects/Renter__c/{record_id}"
	try:
		response = requests.patch(url, headers=headers, json=renter_data)
		response.raise_for_status()  # エラーチェック
		logging.info(f"Record updated successfully: {record_id}")
		return True
	except requests.exceptions.HTTPError as e:
		logging.error(f"HTTP Error: {e}")
		logging.error(f"Response content: {response.text}")
		return False

def create_new_account(instance_url, headers, guarantee_name):
	"""新しい取引先(Account__c)を作成"""
	url = f"{instance_url}/services/data/v54.0/sobjects/Account"
	account_data = {
		"Name": guarantee_name,
		"RentInsuranceCompany__c": True
		}
	try:
		response = requests.post(url, headers=headers, json=account_data)
		response.raise_for_status()
		created_account = response.json()
		logging.info(f"Created new Account: {created_account}")
		return created_account.get("id")
	except requests.exceptions.RequestException as e:
		logging.error(f"Error creating new Account: {e}")
		return None

def find_matching_company(instance_url, headers, guarantee_name):
	"""保証会社名に一致する取引先を検索"""
	query = f"SELECT Id FROM Account WHERE Name = '{guarantee_name}' AND RentInsuranceCompany__c = True"
	url = f"{instance_url}/services/data/v54.0/query?q={query}"
	try:
		response = requests.get(url, headers=headers)
		response.raise_for_status()
		accounts = response.json().get("records", [])
		return accounts[0]["Id"] if accounts else None
	except requests.exceptions.RequestException as e:
		logging.error(f"Error querying Account: {e}")
		return None

def process_guarantee_plan(appjson, instance_url, headers):
	"""保証プランを処理"""
	guarantee_data = appjson.get("guarantee", {})		#guaranteeエリアのデータを取得
	# guaranteeエリアが空の場合、保証プランなしで終了
	if not guarantee_data:
		logging.warning("保証プランなし")
		return None	
	
	#guaranteeエリアが空じゃない場合、保証プラン情報を取得
	guarantee_name = guarantee_data.get("name")		#保証会社名を取得
	guarantee_plan_id = guarantee_data.get("plan_id")	#保証プランidを取得
		
	# 保証プランがSF上に存在するかチェック
	plan_record_id = get_matching_plan_id(guarantee_plan_id, instance_url, headers)
	if plan_record_id:
		return plan_record_id

	# 保証プランがSF上にない場合は会社名を比較
	company_id = find_matching_company(instance_url, headers, guarantee_name)
	if not company_id:
		# 一致する会社がなければ新しい取引先を作成
		company_id = create_new_account(instance_url, headers, guarantee_name)
	
	if not company_id:
		logging.error("新しい取引先の作成に失敗しました。")
		return None

	# 新しい保証プランを作成
	url = f"{instance_url}/services/data/v54.0/sobjects/GuaranteePlan__c"
	new_plan_data = {
		"ExternalId__c": guarantee_plan_id,
		"PlanName__c": guarantee_data.get("plan_name"),
		"ExternalCompanyName__c": guarantee_name,
		"Company__c": company_id
	}
	try:
		response = requests.post(url, headers=headers, json=new_plan_data)
		response.raise_for_status()
		created_plan = response.json()
		logging.info(f"Created new GuaranteePlan: {created_plan}")
		return created_plan.get("id")
	except requests.exceptions.RequestException as e:
		logging.error(f"Error creating new GuaranteePlan: {e}")
		return None


def get_matching_plan_id(plan_code, instance_url, headers):
	"""保証プラン名で一致する保証プランIDを取得"""
	if not plan_code:
		return None

	query = f"SELECT Id FROM GuaranteePlan__c WHERE ExternalId__c = '{plan_code}'"
	url = f"{instance_url}/services/data/v54.0/query?q={query}"
	logging.info(f"Querying Salesforce for GuaranteePlan: {url}")

	try:
		response = requests.get(url, headers=headers)
		response.raise_for_status()
		plans = response.json().get("records", [])
		return plans[0]["Id"] if plans else None
	except requests.exceptions.RequestException as e:
		logging.error(f"Error querying Salesforce for GuaranteePlan: {e}")
		return None


def check_duplicate_record(instance_url, headers, renter_data):
	"""賃借人オブジェクト内の重複チェック"""
	if renter_data["RenterType__c"] == "法人":
		query = (
			f"SELECT Id FROM Renter__c WHERE CorporateNumber__c = {renter_data.get('CorporateNumber__c')}.0 "
			f"AND RenterType__c = '{renter_data.get('RenterType__c')}'"
		)
	else:
		query = (
			f"SELECT Id FROM Renter__c WHERE LastName__c = '{renter_data.get('LastName__c')}' "
			f"AND RenterType__c = '{renter_data.get('RenterType__c')}' "
			f"AND FirstName__c = '{renter_data.get('FirstName__c')}' "
			f"AND Birthday__c = {renter_data.get('Birthday__c')}"
		)
	url = f"{instance_url}/services/data/v54.0/query?q={query}"

	try:
		response = requests.get(url, headers=headers)
		if response.status_code >= 400:
			logging.error(f"Salesforce Error: {response.json()}")
			response.raise_for_status()
		records = response.json().get("records", [])
		return records[0]["Id"] if records else None
		if records:
			record_id = records[0]["Id"]
			logging.info(f"Duplicate record found: {record_id}, updating...")
			update_success = update_renter_record(instance_url, headers, record_id, renter_data)
			if update_success:
				return record_id  # 更新が成功した場合はレコード ID を返す
			else:
				logging.error("Failed to update existing record.")
				return None
		return None  # 重複がない場合は None を返す
	except requests.exceptions.RequestException as e:
		logging.error(f"HTTP Request failed: {e}")
		raise

def process_tenant_data(appjson, renter_type, tenant_key, instance_url, sf_headers, app_data, resident_key):
	"""
	入居者データを処理し、必要な場合に重複チェックやレコード作成を行い、app_data に反映する。
	"""
	# 入居者データをマッピング
	tenant_data = map_variables(appjson, RENTER_COLUMNS_MAPPING[renter_type][tenant_key])
	tenant_data["RenterType__c"] = "個人"

	# LastName__c が None の場合は処理をスキップ
	if not tenant_data.get("LastName__c"):
		logging.info(f"Skipping {tenant_key} due to missing LastName__c")
		return

	# 重複チェックとレコード作成
	tenant_id = check_duplicate_record(instance_url, sf_headers, tenant_data) or create_renter_record(instance_url, sf_headers, tenant_data)

	# app_data に反映
	app_data[resident_key] = tenant_id
	logging.info(f"{resident_key} processed with ID: {tenant_id}")

def create_renter_record(instance_url, headers, renter_data):
	"""新しい Renter__c レコードを作成し、その ID を返す"""
	url = f"{instance_url}/services/data/v54.0/sobjects/Renter__c"
	try:
		response = requests.post(url, headers=headers, json=renter_data)
		response.raise_for_status()  # エラーチェック
		created_record = response.json()  # 作成されたレコードのレスポンスを取得
		logging.info(f"Record created successfully: {created_record}")
		return created_record.get('id')  # 作成されたレコードの詳細を返す
	except requests.exceptions.HTTPError as e:
		logging.error(f"HTTP Error: {e}")
		logging.error(f"Response content: {response.text}")
		raise  # エラーを呼び出し元に伝える

def find_existing_store_branch(auth_id, instance_url, headers):
	"""auth_idで既存のStoreBranch__cレコードを検索"""
	query = f"SELECT Id FROM StoreBranch__c WHERE ExternalId__c = '{auth_id}'"
	url = f"{instance_url}/services/data/v54.0/query?q={query}"
	try:
		response = requests.get(url, headers=headers)
		response.raise_for_status()
		records = response.json().get("records", [])
		return records[0]["Id"] if records else None
	except requests.exceptions.RequestException as e:
		logging.error(f"Error querying StoreBranch__c: {e}")
		return None

def split_company_and_branch(lines):
	"""会社名と支店名を分割"""
	results = []
	# 正規表現: 株式会社を含む部分を会社名、それ以降を支店名として分割
	pattern = r"^(.*?株式会社(?: [^本店]*)?)\s*(本店|.*店)?$"
	
	for line in lines:
		if not isinstance(line, str):  # 入力が文字列でない場合の処理
			logging.warning(f"Invalid line input for splitting: {line}")
			results.append((line, ""))  # デフォルト値で追加
			continue
		match = re.match(pattern, line)
		if match:
			company_name = match.group(1).strip()
			branch_name = match.group(2).strip() if match.group(2) else ""
			results.append((company_name, branch_name))
		else:
			# マッチしない場合はそのまま返す
			results.append((line, ""))
	return results

def process_broker_info(broker_data, instance_url, headers):
	"""仲介会社情報を処理"""
	if not broker_data:
		logging.warning("brokerデータが存在しません。")
		return None

	auth_id = broker_data.get("auth_id")
	broker_name = broker_data.get("company_name")
	phone_number = broker_data.get("fixed_phone_number")
	zipcode = broker_data.get("zipcode")
	address = broker_data.get("address")

	#logging.info(f"broker_data={broker_data}")
	if not auth_id :
		logging.warning("必要な仲介会社情報が不足しています。")
		return None

	# broker_company_nameを分割して会社名と支店名を取得
	company_branch = split_company_and_branch([broker_name])
	company_name, branch_name = company_branch[0] if company_branch else (broker_name, "")

	# Salesforce上で既存のStoreBranch__cレコードを検索
	existing_record_id = find_existing_store_branch(auth_id, instance_url, headers)
	if existing_record_id:
		logging.info(f"既存のStoreBranch__cレコードが見つかりました: {existing_record_id}")
		return existing_record_id

	# 新しいStoreBranch__cレコードを作成
	store_branch_data = {
		"ExternalId__c": auth_id,
		"LicenseName__c": company_name,
		"StoreBranchName__c": branch_name,
		"LicenseOfficeTel__c": phone_number,
		"LicenseOfficeLocation__c": f"{zipcode} {address}"
	}
	try:
		url = f"{instance_url}/services/data/v54.0/sobjects/StoreBranch__c"
		response = requests.post(url, headers=headers, json=store_branch_data)
		response.raise_for_status()
		created_record = response.json()
		logging.info(f"Created new StoreBranch__c record: {created_record}")
		return created_record.get("id")
	except requests.exceptions.RequestException as e:
		logging.error(f"Error creating new StoreBranch__c record: {e}")
		return None

def find_existing_housing_agency(corporate_number, instance_url, headers):
	"""法人番号で既存の社宅代行会社取引先を検索"""
	query = f"SELECT Id FROM Account WHERE ExternalId__c = '{corporate_number}'"
	url = f"{instance_url}/services/data/v54.0/query?q={query}"
	try:
		response = requests.get(url, headers=headers)
		response.raise_for_status()
		accounts = response.json().get("records", [])
		return accounts[0]["Id"] if accounts else None
	except requests.exceptions.RequestException as e:
		logging.error(f"Error querying housing agency: {e}")
		return None

def create_housing_agency(agency_data, instance_url, headers):
	"""新しい社宅代行会社取引先を作成"""
	url = f"{instance_url}/services/data/v54.0/sobjects/Account"
	try:
		response = requests.post(url, headers=headers, json=agency_data)
		response.raise_for_status()
		created_account = response.json()
		logging.info(f"Created new housing agency: {created_account}")
		return created_account.get("id")
	except requests.exceptions.RequestException as e:
		logging.error(f"Error creating new housing agency: {e}")
		return None

def process_housing_agency(appjson, instance_url, headers):
	"""社宅代行会社情報を処理"""
	if not appjson.get("corp"):
		logging.info("RenterType is not '法人', skipping housing agency processing.")
		return None

	# 社宅代行情報を取得
	agency_name = None
	corporate_number = None
	
	
	for entry_body in appjson.get("entry_bodies", []):
		if entry_body.get("name") == "corp_company_housing_agency":
			agency_name = entry_body.get("text")
		elif entry_body.get("name") == "corp_company_housing_nationaltaxagency_corporate_number":
			corporate_number = entry_body.get("text")

	if not agency_name:
		logging.warning("Missing housing agency data. Skipping processing.")
		return None

	# 既存の社宅代行会社を検索
	existing_agency_id = find_existing_housing_agency(corporate_number, instance_url, headers)
	if existing_agency_id:
		logging.info(f"Found existing housing agency: {existing_agency_id}")
		return existing_agency_id

	# 新しい社宅代行会社を作成
	agency_data = {
		"Name": agency_name,
		"ExternalId__c": corporate_number,
	}
	logging.info(f"agency_data = {agency_data }")
	return create_housing_agency(agency_data, instance_url, headers)

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
	headers = {'Authorization': ITANDI_TOKEN}

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
		
	# STEP 3: 契約者情報の重複チェック
	#アクセストークンを取得してSFAPIのヘッダを構築
	access_token, instance_url = get_salesforce_token()
	sf_headers = {
		'Authorization': f'Bearer {access_token}',
		'Content-Type': 'application/json',
	}
	
	# STEP 4: 個人/法人のマッピング表を選択
	# 賃借人オブジェクトから個人/法人に分けて契約者のマッピング表を選択
	renter_type = "法人" if appjson.get("corp") else "個人"
	renter_data =  map_variables(appjson, RENTER_COLUMNS_MAPPING[renter_type]["契約者"])
	renter_data["RenterType__c"] = renter_type


	# STEP 5: 保証プランの紐づけ
	try:
		plan_record_id = process_guarantee_plan(appjson, instance_url, sf_headers)
		#app_data に保証プラン ID を設定
		logging.info(f"GuaranteePlan__c set to: {plan_record_id}")
	except Exception as e:
		logging.error(f"Error processing guarantee plan: {e}")
		raise	

	# STEP6: 仲介会社情報の処理
	broker_data = appjson.get("broker", {})
	try:
		broker_record_id = process_broker_info(broker_data, instance_url, sf_headers)
		logging.info(f"AccountObjCategory__c set to: {broker_record_id}")
	except Exception as e:
		logging.error(f"Error processing broker info: {e}")
		raise

	# STEP 7: 社宅代行会社情報の処理
	try:
		agent_id = process_housing_agency(appjson, instance_url, sf_headers)
		logging.info(f"Agent__c set to: {agent_id}")
	except Exception as e:
		logging.error(f"Error processing housing agency: {e}")
		agent_id = None

	# STEP 8: 申込情報の更新	
	# 申込情報の構築
	app_data = map_variables(appjson, APPLICATION_COLUMNS_MAPPING)
	app_data["IndividualCorporation__c"]=renter_type
	app_data["GuaranteePlan__c"]=plan_record_id
	app_data["AccountObjCategory__c"] = broker_record_id
	app_data["BrokerCompany__c"] = broker_data.get('company_name')
	app_data["ResponsiblePersonPhoneNumber__c"] = broker_data.get('phone_number')
	app_data["ResponsiblePerson__c"] = broker_data.get('name')
	app_data["EResponsiblePersonEmail__c"] = broker_data.get('email')
	app_data["Agent__c"] = agent_id

	# 契約者重複チェックと重複しない場合に新規作成
	contractor_id = check_duplicate_record(instance_url, sf_headers, renter_data) or create_renter_record(instance_url, sf_headers, renter_data)
	app_data["Contractor__c"]=contractor_id

	# 入居者重複チェックと重複しない場合に新規作成
	for i in range(1, 6):  # 入居者 1〜5 をループ処理
		tenant_key = f"入居者{i}"
		resident_key = f"Resident{i}__c"
		process_tenant_data(appjson, renter_type, tenant_key, instance_url, sf_headers, app_data, resident_key)	


	# 申込オブジェクトの更新
	app_url = f"{instance_url}/services/data/v54.0/sobjects/Application__c/{record_id}"
	app_response = requests.patch(app_url, headers=sf_headers, json=app_data)
	if app_response.status_code != 204:
		error_message = app_response.json() if app_response.content else {"error": "Unknown error"}
		logging.error(f"Salesforce Application update error: {error_message}")
		return jsonify({"error": error_message}), app_response.status_code

	return '''<script>window.close();</script>''', 200
	

	# IPアドレステスト用URL
	#ipurl = 'http://checkip.dyndns.com/'
	#ipres = requests.get(ipurl)
	#print('IPアドレス：',ipres.text)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)


