from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

SOURCES = {
    "ophim": "https://ophim1.com/api/v1",
    "kkphim": "https://phimapi.com",
    "nguonc": "https://phim.nguonc.com/api"
}

def fetch_json(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://phimapi.com/"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        return resp.json()
    except:
        return None

@app.route('/api/movies')
def handle_request():
    src = request.args.get('src', 'ophim')
    path = request.args.get('path', '')
    keyword = request.args.get('keyword', '')
    page = request.args.get('page', '1')
    
    base = SOURCES.get(src)
    if not base: return jsonify({"error": "Invalid source"})

    # Lấy chi tiết phim - Fix logic cho Nguonc và KKPhim
    if path:
        url = f"{base}/film/{path}" if src == "nguonc" else f"{base}/phim/{path}"
        return jsonify(fetch_json(url))
    
    # Tìm kiếm phim
    if keyword:
        if src == "nguonc": url = f"{base}/films/search?keyword={keyword}&page={page}"
        elif src == "kkphim": url = f"{base}/v1/api/tim-kiem?keyword={keyword}&page={page}"
        else: url = f"{base}/tim-kiem?keyword={keyword}&page={page}"
        return jsonify(fetch_json(url))
        
    # Mặc định lấy phim mới
    url = f"{base}/films/phim-moi-cap-nhat?page={page}" if src == "nguonc" else f"{base}/danh-sach/phim-moi-cap-nhat?page={page}"
    return jsonify(fetch_json(url))
