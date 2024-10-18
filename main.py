import requests
from flask import Flask
 
 
app = Flask(__name__)
 
# DynDNS の URL
url = 'https://staging.moushikomi-uketsukekun.com/maintenance_company/api/v2/entry_heads'
 
 
@app.route('/')
def ip_check():
 
    # HTTP リクエストを送信
    res = requests.get(url)
    
    # レスポンスをブラウザ上に表示
    return res.text
 
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)