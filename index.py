from flask import Flask, request, jsonify, make_response
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Proxy đến API OPhim
@app.route('/api/proxy')
def proxy():
    path = request.args.get('path', '')
    if not path:
        return jsonify({"error": "No path provided"}), 400
        
    target_url = f"https://ophim1.com/api/v1/{path}"
    
    try:
        # Gọi sang OPhim lấy dữ liệu
        response = requests.get(target_url, timeout=10)
        data = response.json()
        
        # Trả về dữ liệu kèm cấu hình Cache để tăng tốc
        res = make_response(jsonify(data))
        res.headers['Cache-Control'] = 's-maxage=3600, stale-while-revalidate=600'
        return res
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Hàm bắt buộc để Vercel nhận diện Flask app
def handler(event, context):
    return app(event, context)
