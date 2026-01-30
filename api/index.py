from flask import Flask, request, jsonify, make_response
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/proxy')
def proxy():
    source = request.args.get('src', 'kkphim')
    path = request.args.get('path', '')
    page = request.args.get('page', '1')
    keyword = request.args.get('keyword', '')

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://phimapi.com/"
    }

    try:
        if source == 'nguonc':
            base = "https://phim.nguonc.com/api"
            # NguonC dùng film/{slug} cho chi tiết
            url = f"{base}/{path}" if path else (f"{base}/films/search?keyword={keyword}&page={page}" if keyword else f"{base}/films/phim-moi-cap-nhat?page={page}")
        elif source == 'kkphim':
            base = "https://phimapi.com"
            # KKPhim BẮT BUỘC phải có tiền tố /phim/ để trả về danh sách tập
            if path:
                clean_slug = path.split('/')[-1] # Lấy slug cuối cùng để tránh trùng lặp tiền tố
                url = f"{base}/phim/{clean_slug}"
            elif keyword:
                url = f"{base}/v1/api/tim-kiem?keyword={keyword}&page={page}"
            else:
                url = f"{base}/danh-sach/phim-moi-cap-nhat?page={page}"
        else:
            base = "https://ophim1.com/api/v1"
            url = f"{base}/{path}" if path else (f"{base}/tim-kiem?keyword={keyword}&page={page}" if keyword else f"{base}/danh-sach/phim-moi-cap-nhat?page={page}")

        resp = requests.get(url, headers=headers, timeout=10)
        return make_response(jsonify(resp.json()))
    except Exception as e:
        return jsonify({"error": str(e), "items": []})
