from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
from functools import lru_cache

app = Flask(__name__)
CORS(app)

@lru_cache(maxsize=128)
def fetch_ophim(url):
    headers = {"accept": "application/json", "User-Agent": "Mozilla/5.0"}
    try:
        return requests.get(url, headers=headers, timeout=10).json()
    except:
        return {"status": False, "message": "API Ophim error"}

@app.route('/api/ophim')
def handle():
    slug = request.args.get('path')
    kw = request.args.get('keyword')
    page = request.args.get('page', '1')
    
    if slug: 
        url = f"https://ophim1.com/v1/api/phim/{slug}"
    elif kw: 
        url = f"https://ophim1.com/v1/api/tim-kiem?keyword={kw}&limit=20"
    else: 
        url = f"https://ophim1.com/v1/api/danh-sach/phim-moi-cap-nhat?page={page}"
    
    return jsonify(fetch_ophim(url))
