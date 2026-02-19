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

@app.route('/api/movies')
def handle_request():
    src = request.args.get('src', 'ophim')
    path = request.args.get('path', '')
    keyword = request.args.get('keyword', '')
    base = SOURCES.get(src)

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    try:
        if path:
            # Fix logic lấy chi tiết cho từng nguồn
            url = f"{base}/film/{path}" if src == "nguonc" else f"{base}/phim/{path}"
            resp = requests.get(url, headers=headers, timeout=10).json()
            return jsonify(resp)
        
        if keyword:
            if src == "nguonc": url = f"{base}/films/search?keyword={keyword}"
            elif src == "kkphim": url = f"{base}/v1/api/tim-kiem?keyword={keyword}"
            else: url = f"{base}/tim-kiem?keyword={keyword}"
        else:
            url = f"{base}/films/phim-moi-cap-nhat" if src == "nguonc" else f"{base}/danh-sach/phim-moi-cap-nhat"
            
        return jsonify(requests.get(url, headers=headers).json())
    except Exception as e:
        return jsonify({"error": str(e)})
