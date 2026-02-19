from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
from functools import lru_cache

app = Flask(__name__)
CORS(app)

@lru_cache(maxsize=128)
def fetch_nguonc(url):
    try:
        return requests.get(url, timeout=10).json()
    except:
        return {"status": False}

@app.route('/api/nguonc')
def handle():
    slug = request.args.get('path')
    kw = request.args.get('keyword')
    page = request.args.get('page', '1')
    
    if slug: 
        url = f"https://phim.nguonc.com/api/film/{slug}"
    elif kw: 
        url = f"https://phim.nguonc.com/api/films/search?keyword={kw}&page={page}"
    else: 
        url = f"https://phim.nguonc.com/api/films/phim-moi-cap-nhat?page={page}"
    
    return jsonify(fetch_nguonc(url))
