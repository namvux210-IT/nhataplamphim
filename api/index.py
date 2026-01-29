from flask import Flask, request, jsonify, make_response
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/proxy')
def proxy():
    path = request.args.get('path', 'danh-sach/phim-moi-cap-nhat')
    path = path.lstrip('/')
    
    # CẬP NHẬT: OPhim đôi khi dùng api/v1, đôi khi không. 
    # Chúng ta sẽ thử cấu trúc link trực tiếp này:
    target_url = f"https://ophim1.com/api/v1/{path}"
    
    try:
        response = requests.get(target_url, timeout=10)
        # Nếu link trên lỗi 404, thử link dự phòng không có 'v1'
        if response.status_code == 404:
            target_url = f"https://ophim1.com/{path}"
            response = requests.get(target_url, timeout=10)
            
        data = response.json()
        res = make_response(jsonify(data))
        res.headers['Cache-Control'] = 's-maxage=3600, stale-while-revalidate=600'
        return res
    except Exception as e:
        return jsonify({"status": False, "msg": str(e)}), 500
