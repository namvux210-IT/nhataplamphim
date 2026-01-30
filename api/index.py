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
    year = request.args.get('year', '') # Nhận tham số năm từ frontend
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://phim.nguonc.com/"
    }

    if source == 'nguonc':
        base_url = "https://phim.nguonc.com/api"
        # Nguonc không có lọc năm riêng, nên ta dùng năm làm từ khóa nếu không có tên phim
        search_key = keyword if keyword else year
        if search_key:
            target_url = f"{base_url}/films/search?keyword={search_key}&page={page}"
        else:
            target_url = f"{base_url}/films/phim-moi-cap-nhat?page={page}"
            
    elif source == 'kkphim':
        # KKPhim hỗ trợ lọc năm cực chuẩn qua API v1
        if keyword or year:
            target_url = f"https://phimapi.com/v1/api/tim-kiem?keyword={keyword}&year={year}&page={page}&limit=20"
        else:
            target_url = f"https://phimapi.com/danh-sach/phim-moi-cap-nhat?page={page}"
            
    else: # OPhim
        target_url = f"https://ophim1.com/api/v1/danh-sach/phim-moi-cap-nhat?page={page}"
        if keyword: target_url += f"&keyword={keyword}"

    try:
        response = requests.get(target_url, headers=headers, timeout=10)
        return make_response(jsonify(response.json()))
    except:
        return jsonify({"items": []})
