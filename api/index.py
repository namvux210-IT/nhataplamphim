from flask import Flask, request, jsonify, make_response
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/proxy')
def proxy():
    # Lấy path từ query string
    path = request.args.get('path', 'danh-sach/phim-moi-cap-nhat')
    target_url = f"https://ophim1.com/api/v1/{path}"
    
    try:
        response = requests.get(target_url, timeout=10)
        data = response.json()
        
        # Tạo response và thiết lập Cache để load nhanh hơn
        res = make_response(jsonify(data))
        res.headers['Cache-Control'] = 's-maxage=3600, stale-while-revalidate=600'
        return res
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Vercel sẽ tự động tìm biến 'app' này để chạy
