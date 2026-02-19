from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/nguonc')
def handle():
    kw = request.args.get('keyword', '')
    slug = request.args.get('path', '')
    
    if slug:
        url = f"https://phim.nguonc.com/api/film/{slug}"
    else:
        # NguonC dùng endpoint /films/search cho tìm kiếm
        url = f"https://phim.nguonc.com/api/films/search?keyword={kw}"
    
    try:
        return jsonify(requests.get(url, timeout=10).json())
    except:
        return jsonify({"status": False, "data": []})
