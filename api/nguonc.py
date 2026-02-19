from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/nguonc')
def handle():
    path = request.args.get('path', '')
    keyword = request.args.get('keyword', '')
    headers = {"User-Agent": "Mozilla/5.0"}
    
    if path: url = f"https://phim.nguonc.com/api/film/{path}"
    elif keyword: url = f"https://phim.nguonc.com/api/films/search?keyword={keyword}"
    else: url = f"https://phim.nguonc.com/api/films/phim-moi-cap-nhat"
    
    return jsonify(requests.get(url, headers=headers).json())
