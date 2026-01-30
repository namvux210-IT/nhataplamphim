from flask import Flask, request, jsonify, make_response
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/proxy')
def proxy():
    path = request.args.get('path', '')
    source = request.args.get('src', 'ophim')
    page = request.args.get('page', '1')
    
    # Lấy các tham số lọc nâng cao từ URL web truyền lên
    keyword = request.args.get('keyword', '')
    category = request.args.get('category', '')
    country = request.args.get('country', '')
    year = request.args.get('year', '')

    if source == 'kkphim':
        # Sử dụng Endpoint v1 mới của KKPhim để hỗ trợ lọc
        base_url = "https://phimapi.com/v1/api"
        if 'tim-kiem' in path or keyword:
            target_url = f"{base_url}/tim-kiem?keyword={keyword}&page={page}"
            if category: target_url += f"&category={category}"
            if country: target_url += f"&country={country}"
            if year: target_url += f"&year={year}"
            target_url += "&limit=20"
        else:
            target_url = f"https://phimapi.com/{path}?page={page}"
    elif source == 'nguonc':
        target_url = f"https://phim.nguonc.com/api/films/search?keyword={keyword}&page={page}" if keyword else f"https://phim.nguonc.com/api/{path}?page={page}"
    else: # OPhim
        target_url = f"https://ophim1.com/api/v1/{path}?page={page}"
        if keyword: target_url += f"&keyword={keyword}"

    try:
        response = requests.get(target_url, timeout=10)
        return make_response(jsonify(response.json()))
    except:
        return jsonify({"error": "Lỗi server"}), 500
