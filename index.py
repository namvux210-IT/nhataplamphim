from flask import Flask, request, jsonify, make_response
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

BASE_URL = "https://ophim1.com/api/v1"

@app.route('/api/proxy')
def proxy():
    path = request.args.get('path', 'danh-sach/phim-moi-cap-nhat')
    try:
        # Gọi sang OPhim lấy dữ liệu
        response = requests.get(f"{BASE_URL}/{path}", timeout=10)
        data = response.json()
        
        # Tạo response và thiết lập Cache 1 giờ (3600 giây)
        res = make_response(jsonify(data))
        res.headers['Cache-Control'] = 's-maxage=3600, stale-while-revalidate=600'
        return res
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run()