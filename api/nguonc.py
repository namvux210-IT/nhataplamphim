from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/nguonc')
def handle():
    slug = request.args.get('path')
    kw = request.args.get('keyword')
    # NguonC dùng endpoint /films/search cho tìm kiếm và /film/ cho chi tiết
    if slug: url = f"https://phim.nguonc.com/api/film/{slug}"
    elif kw: url = f"https://phim.nguonc.com/api/films/search?keyword={kw}"
    else: url = f"https://phim.nguonc.com/api/films/phim-moi-cap-nhat"
    
    try:
        resp = requests.get(url, timeout=10)
        return jsonify(resp.json())
    except:
        return jsonify({"status": False})
