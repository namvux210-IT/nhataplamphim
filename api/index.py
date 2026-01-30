from flask import Flask, request, jsonify, make_response
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/proxy')
def proxy():
    source = request.args.get('src', 'ophim')
    page = request.args.get('page', '1')
    keyword = request.args.get('keyword', '')
    path = request.args.get('path', '')

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://phim.nguonc.com/"
    }

    try:
        if source == 'nguonc':
            base = "https://phim.nguonc.com/api"
            if path: target_url = f"{base}/{path}"
            elif keyword: target_url = f"{base}/films/search?keyword={keyword}&page={page}"
            else: target_url = f"{base}/films/phim-moi-cap-nhat?page={page}"

        elif source == 'kkphim':
            base = "https://phimapi.com"
            if path: target_url = f"{base}/{path}"
            elif keyword: target_url = f"{base}/v1/api/tim-kiem?keyword={keyword}&page={page}"
            else: target_url = f"{base}/danh-sach/phim-moi-cap-nhat?page={page}"

        else: # OPhim
            if path: target_url = f"https://ophim1.com/api/v1/{path}"
            else:
                target_url = f"https://ophim1.com/api/v1/danh-sach/phim-moi-cap-nhat?page={page}"
                if keyword: target_url = f"https://ophim1.com/api/v1/tim-kiem?keyword={keyword}&page={page}"

        response = requests.get(target_url, headers=headers, timeout=10)
        return make_response(jsonify(response.json()))
    except:
        return jsonify({"items": []})
