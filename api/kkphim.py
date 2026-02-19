from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/kkphim')
def handle():
    slug, kw = request.args.get('path'), request.args.get('keyword')
    headers = {"Referer": "https://kkphim.vip/", "User-Agent": "Mozilla/5.0"}
    if slug: url = f"https://phimapi.com/phim/{slug}"
    elif kw: url = f"https://phimapi.com/v1/api/tim-kiem?keyword={kw}&limit=20"
    else: url = "https://phimapi.com/danh-sach/phim-moi-cap-nhat?page=1"
    try:
        return jsonify(requests.get(url, headers=headers, timeout=10).json())
    except:
        return jsonify({"status": False})
