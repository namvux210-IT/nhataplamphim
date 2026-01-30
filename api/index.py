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
        # Chuẩn hóa URL cho từng nguồn để tránh lỗi 404 hoặc 500
        if source == 'nguonc':
            base = "https://phim.nguonc.com/api"
            target_url = f"{base}/{path}" if path else (f"{base}/films/search?keyword={keyword}&page={page}" if keyword else f"{base}/films/phim-moi-cap-nhat?page={page}")
        elif source == 'kkphim':
            base = "https://phimapi.com"
            # KKPhim yêu cầu tiền tố /phim/ cho đường dẫn chi tiết
            if path:
                p = path if path.startswith('phim/') else f"phim/{path}"
                target_url = f"{base}/{p}"
            elif keyword:
                target_url = f"{base}/v1/api/tim-kiem?keyword={keyword}&page={page}"
            else:
                target_url = f"{base}/danh-sach/phim-moi-cap-nhat?page={page}"
        else: # OPhim (Dự phòng)
            base = "https://ophim1.com/api/v1"
            target_url = f"{base}/{path}" if path else (f"{base}/tim-kiem?keyword={keyword}&page={page}" if keyword else f"{base}/danh-sach/phim-moi-cap-nhat?page={page}")

        response = requests.get(target_url, headers=headers, timeout=10)
        return make_response(jsonify(response.json()))
    except Exception as e:
        return jsonify({"error": str(e), "items": []})
