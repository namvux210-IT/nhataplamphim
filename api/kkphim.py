from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/kkphim')
def handle():
    kw = request.args.get('keyword', '')
    slug = request.args.get('path', '')
    headers = {"Referer": "https://phimapi.com/", "User-Agent": "Mozilla/5.0"}
    
    if slug:
        url = f"https://phimapi.com/phim/{slug}"
    else:
        # Khớp chính xác với tham số link mẫu bạn gửi
        url = f"https://phimapi.com/v1/api/tim-kiem?keyword={kw}&limit=20"
    
    try:
        return jsonify(requests.get(url, headers=headers, timeout=10).json())
    except:
        return jsonify({"status": False, "data": {"items": []}})
