from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/ophim')
def handle():
    slug = request.args.get('path')
    kw = request.args.get('keyword')
    headers = {"accept": "application/json", "User-Agent": "Mozilla/5.0"}
    
    # Endpoint theo code mẫu của bạn
    if slug: url = f"https://ophim1.com/v1/api/phim/{slug}"
    elif kw: url = f"https://ophim1.com/v1/api/tim-kiem?keyword={kw}"
    else: url = "https://ophim1.com/api/v1/danh-sach/phim-moi-cap-nhat"
    
    try:
        return jsonify(requests.get(url, headers=headers, timeout=10).json())
    except:
        return jsonify({"status": False})
