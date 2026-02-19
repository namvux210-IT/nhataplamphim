from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/kkphim')
def handle():
    slug = request.args.get('path')
    kw = request.args.get('keyword')
    # KKPhim yêu cầu Referer cực kỳ khắt khe để tránh lỗi 'Nguồn bảo trì'
    headers = {
        "Referer": "https://kkphim.vip/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
    }
    
    if slug: url = f"https://phimapi.com/phim/{slug}"
    elif kw: url = f"https://phimapi.com/v1/api/tim-kiem?keyword={kw}&limit=20"
    else: url = f"https://phimapi.com/danh-sach/phim-moi-cap-nhat?page=1"
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        return jsonify(resp.json())
    except:
        return jsonify({"status": False, "message": "API KKPhim Timeout"})
