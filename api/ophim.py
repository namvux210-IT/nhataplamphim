from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/ophim')
def handle():
    path = request.args.get('path', '')
    keyword = request.args.get('keyword', '')
    if path: url = f"https://ophim1.com/api/v1/phim/{path}"
    elif keyword: url = f"https://ophim1.com/api/v1/tim-kiem?keyword={keyword}"
    else: url = f"https://ophim1.com/api/v1/danh-sach/phim-moi-cap-nhat"
    
    return jsonify(requests.get(url).json())
