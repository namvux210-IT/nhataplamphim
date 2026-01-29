from flask import Flask, request, jsonify, make_response
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/proxy')
def proxy():
    path = request.args.get('path', 'danh-sach/phim-moi-cap-nhat')
    source = request.args.get('src', 'ophim') # Nhận nguồn từ Frontend
    path = path.lstrip('/')
    
    # Chọn địa chỉ API dựa trên nguồn phim
    if source == 'kkphim':
        base_url = "https://phimapi.com"
    else:
        # API v1 của OPhim
        base_url = "https://ophim1.com/api/v1"
        
    target_url = f"{base_url}/{path}"
    
    try:
        response = requests.get(target_url, timeout=10)
        data = response.json()
        res = make_response(jsonify(data))
        # Lưu bộ nhớ đệm 1 giờ để web load nhanh
        res.headers['Cache-Control'] = 's-maxage=3600, stale-while-revalidate=600'
        return res
    except Exception as e:
        return jsonify({"error": str(e)}), 500
