from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/nguonc')
def handle():
    slug, kw = request.args.get('path'), request.args.get('keyword')
    if slug: url = f"https://phim.nguonc.com/api/film/{slug}"
    elif kw: url = f"https://phim.nguonc.com/api/films/search?keyword={kw}"
    else: url = "https://phim.nguonc.com/api/films/phim-moi-cap-nhat"
    try:
        return jsonify(requests.get(url, timeout=10).json())
    except:
        return jsonify({"status": False})
