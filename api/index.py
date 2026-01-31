from flask import Flask, request, jsonify, make_response
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/proxy')
def proxy():
    # Ophim API base
    base_url = "https://ophim1.com/api/v1"
    
    path = request.args.get('path', '')
    keyword = request.args.get('keyword', '')
    page = request.args.get('page', '1')

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        if path:
            # Lấy chi tiết phim: /phim/{slug}
            url = f"{base_url}/phim/{path}"
        elif keyword:
            # Tìm kiếm phim: /tim-kiem?keyword={keyword}
            url = f"{base_url}/tim-kiem?keyword={keyword}&page={page}"
        else:
            # Danh sách phim mới nhất
            url = f"{base_url}/danh-sach/phim-moi-cap-nhat?page={page}"

        resp = requests.get(url, headers=headers, timeout=10)
        return make_response(jsonify(resp.json()))
    except Exception as e:
        return jsonify({"error": str(e), "status": False})
