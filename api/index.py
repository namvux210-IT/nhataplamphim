from flask import Flask, request, jsonify, make_response
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/proxy')
def proxy():
    path = request.args.get('path', 'danh-sach/phim-moi-cap-nhat')
    # Thêm tham số source, mặc định là ophim
    source = request.args.get('src', 'ophim')
    path = path.lstrip('/')
    
    # Chọn domain dựa trên nguồn
    if source == 'kkphim':
        base_url = "https://phimapi.com" # API của KKPhim
    else:
        base_url = "https://ophim1.com/api/v1" # API của OPhim
        
    target_url = f"{base_url}/{path}"
    
    try:
        response = requests.get(target_url, timeout=10)
        data = response.json()
        res = make_response(jsonify(data))
        res.headers['Cache-Control'] = 's-maxage=3600, stale-while-revalidate=600'
        return res
    except Exception as e:
        return jsonify({"error": str(e)}), 500
