from flask import Flask, request, jsonify, make_response
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/proxy')
def proxy():
    path = request.args.get('path', 'danh-sach/phim-moi-cap-nhat')
    source = request.args.get('src', 'ophim')
    page = request.args.get('page', '1')
    
    # Xử lý Endpoint cho từng nguồn
    if source == 'nguonc':
        base_url = "https://phim.nguonc.com/api"
        if 'tim-kiem' in path or 'search' in path:
            keyword = request.args.get('keyword', '')
            target_url = f"{base_url}/films/search?keyword={keyword}&page={page}"
        elif 'danh-sach' in path:
            target_url = f"{base_url}/films/phim-moi-cap-nhat?page={page}"
        else:
            target_url = f"{base_url}/{path}"
    elif source == 'kkphim':
        base_url = "https://phimapi.com"
        target_url = f"{base_url}/{path}?page={page}"
        if 'keyword' in request.args:
            target_url += f"&keyword={request.args.get('keyword')}"
    else: # OPhim
        base_url = "https://ophim1.com/api/v1"
        target_url = f"{base_url}/{path}?page={page}"
        if 'keyword' in request.args:
            target_url += f"&keyword={request.args.get('keyword')}"

    try:
        response = requests.get(target_url, timeout=10)
        data = response.json()
        res = make_response(jsonify(data))
        res.headers['Cache-Control'] = 's-maxage=60, stale-while-revalidate=30'
        return res
    except Exception as e:
        return jsonify({"error": str(e)}), 500
