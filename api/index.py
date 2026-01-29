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
    
    path = path.lstrip('/')
    # Kết hợp path với page
    if '?' in path:
        final_path = f"{path}&page={page}"
    else:
        final_path = f"{path}?page={page}"

    base_url = "https://phimapi.com" if source == 'kkphim' else "https://ophim1.com/api/v1"
    target_url = f"{base_url}/{final_path}"
    
    try:
        response = requests.get(target_url, timeout=10)
        data = response.json()
        res = make_response(jsonify(data))
        res.headers['Cache-Control'] = 's-maxage=60, stale-while-revalidate=30'
        return res
    except Exception as e:
        return jsonify({"error": str(e)}), 500
