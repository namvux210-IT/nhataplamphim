from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
from functools import lru_cache

app = Flask(__name__)
CORS(app)

@lru_cache(maxsize=128)
def fetch_kk(url):
    headers = {"Referer": "https://kkphim.vip/", "User-Agent": "Mozilla/5.0"}
    try:
        return requests.get(url, headers=headers, timeout=10).json()
    except:
        return {"status": False}

@app.route('/api/kkphim')
def handle():
    slug = request.args.get('path')
    kw = request.args.get('keyword')
    page = request.args.get('page', '1')
    
    if slug: 
        url = f"https://phimapi.com/phim/{slug}"
    elif kw: 
        url = f"https://phimapi.com/v1/api/tim-kiem?keyword={kw}&page={page}&limit=20"
    else: 
        url = f"https://phimapi.com/danh-sach/phim-moi-cap-nhat?page={page}"
    
    return jsonify(fetch_kk(url))
