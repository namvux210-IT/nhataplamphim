from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

SOURCES = {
    "kkphim": "https://phimapi.com",
    "nguonc": "https://phim.nguonc.com/api"
}

def fetch_json(url, src):
    # Giả lập header để server phim không chặn trình phát
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://phimapi.com/" if src == "kkphim" else "https://phim.nguonc.com/",
        "Origin": "https://phimapi.com"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        return resp.json()
    except:
        return None

@app.route('/api/movies')
def handle_request():
    src = request.args.get('src', 'kkphim')
    path = request.args.get('path', '')
    keyword = request.args.get('keyword', '')
    page = request.args.get('page', '1')
    
    base = SOURCES.get(src)
    if not base: return jsonify({"error": "Invalid Source"})

    if path:
        url = f"{base}/film/{path}" if src == "nguonc" else f"{base}/phim/{path}"
        return jsonify(fetch_json(url, src))
    
    if keyword:
        url = f"{base}/films/search?keyword={keyword}&page={page}" if src == "nguonc" else f"{base}/v1/api/tim-kiem?keyword={keyword}&page={page}"
    else:
        url = f"{base}/films/phim-moi-cap-nhat?page={page}" if src == "nguonc" else f"{base}/danh-sach/phim-moi-cap-nhat?page={page}"
            
    return jsonify(fetch_json(url, src))
