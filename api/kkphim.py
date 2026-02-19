from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/kkphim')
def handle():
    path = request.args.get('path', '')
    keyword = request.args.get('keyword', '')
    page = request.args.get('page', '1')
    headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://phimapi.com/"}
    
    if path: url = f"https://phimapi.com/phim/{path}"
    elif keyword: url = f"https://phimapi.com/v1/api/tim-kiem?keyword={keyword}&limit=20"
    else: url = f"https://phimapi.com/danh-sach/phim-moi-cap-nhat?page={page}"
    
    return jsonify(requests.get(url, headers=headers).json())
