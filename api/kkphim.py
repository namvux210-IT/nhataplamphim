from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/kkphim')
def handle():
    slug = request.args.get('path')
    kw = request.args.get('keyword')
    headers = {"Referer": "https://phimapi.com/", "User-Agent": "Mozilla/5.0"}
    # Link mẫu: https://phimapi.com/phim/[slug]
    if slug: url = f"https://phimapi.com/phim/{slug}"
    elif kw: url = f"https://phimapi.com/v1/api/tim-kiem?keyword={kw}"
    else: url = "https://phimapi.com/danh-sach/phim-moi-cap-nhat?page=1"
    
    try:
        return jsonify(requests.get(url, headers=headers, timeout=10).json())
    except:
        return jsonify({"status": False})
