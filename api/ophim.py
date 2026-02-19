from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/ophim')
def handle():
    kw = request.args.get('keyword', '')
    slug = request.args.get('path', '')
    headers = {"accept": "application/json", "User-Agent": "Mozilla/5.0"}
    
    if slug:
        url = f"https://ophim1.com/api/v1/phim/{slug}"
    else:
        url = f"https://ophim1.com/v1/api/tim-kiem?keyword={kw}"
        
    try:
        return jsonify(requests.get(url, headers=headers, timeout=10).json())
    except:
        return jsonify({"status": False, "data": {"items": []}})
