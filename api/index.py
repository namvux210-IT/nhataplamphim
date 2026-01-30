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
    keyword = request.args.get('keyword', '')
    
    # Headers giúp vượt qua hàng rào bảo mật của NguonC
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://phim.nguonc.com/"
    }

    if source == 'nguonc':
        base_url = "https://phim.nguonc.com/api"
        if keyword:
            target_url = f"{base_url}/films/search?keyword={keyword}&page={page}"
        elif 'film/' in path:
            target_url = f"{base_url}/{path}"
        else:
            target_url = f"{base_url}/films/phim-moi-cap-nhat?page={page}"
    elif source == 'kkphim':
        if keyword:
            target_url = f"https://phimapi.com/v1/api/tim-kiem?keyword={keyword}&page={page}"
        elif 'phim/' in path:
            target_url = f"https://phimapi.com/{path}"
        else:
            target_url = f"https://phimapi.com/danh-sach/phim-moi-cap-nhat?page={page}"
    else: # OPhim
        if 'phim/' in path:
            target_url = f"https://ophim1.com/api/v1/{path}"
        else:
            target_url = f"https://ophim1.com/api/v1/danh-sach/phim-moi-cap-nhat?page={page}"
            if keyword: target_url += f"&keyword={keyword}"

    try:
        response = requests.get(target_url, headers=headers, timeout=10)
        return make_response(jsonify(response.json()))
    except:
        return jsonify({"items": [], "status": False})
