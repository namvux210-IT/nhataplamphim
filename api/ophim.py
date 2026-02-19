from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/ophim')
def handle():
    slug, kw = request.args.get('path'), request.args.get('keyword')
    if slug: url = f"https://ophim1.com/api/v1/phim/{slug}"
    elif kw: url = f"https://ophim1.com/api/v1/tim-kiem?keyword={kw}"
    else: url = "https://ophim1.com/api/v1/danh-sach/phim-moi-cap-nhat"
    try:
        return jsonify(requests.get(url, timeout=10).json())
    except:
        return jsonify({"status": False})
