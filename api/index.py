from flask import Flask, request, jsonify, make_response
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
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        resp = requests.get(url, headers=headers, timeout=10)
        return resp.json()
    except:
        return None

@app.route('/api/movies')
def handle_request():
    src = request.args.get('src', 'ophim')
    path = request.args.get('path', '')
    keyword = request.args.get('keyword', '')
    
    base = SOURCES.get(src)
    if path:
        # Lấy chi tiết phim để trích xuất link embed
        url = f"{base}/film/{path}" if src == "nguonc" else f"{base}/phim/{path}"
        return jsonify(fetch_json(url))
    
    if keyword:
        # Tìm kiếm phim từ nguồn tương ứng
        if src == "nguonc": url = f"{base}/films/search?keyword={keyword}"
        elif src == "kkphim": url = f"{base}/v1/api/tim-kiem?keyword={keyword}"
        else: url = f"{base}/tim-kiem?keyword={keyword}"
        return jsonify(fetch_json(url))
        
    url = f"{base}/films/phim-moi-cap-nhat" if src == "nguonc" else f"{base}/danh-sach/phim-moi-cap-nhat"
    return jsonify(fetch_json(url))
