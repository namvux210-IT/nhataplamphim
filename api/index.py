from flask import Flask, request, jsonify, make_response
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/proxy')
def proxy():
    path = request.args.get('path', 'danh-sach/phim-moi-cap-nhat')
    target_url = f"https://ophim1.com/api/v1/{path}"
    
    try:
        response = requests.get(target_url, timeout=10)
        data = response.json()
        
        res = make_response(jsonify(data))
        # Thiết lập Cache để Vercel Edge tải nhanh
        res.headers['Cache-Control'] = 's-maxage=3600, stale-while-revalidate=600'
        return res
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# BẮT BUỘC: Thêm dòng này nếu Vercel vẫn báo lỗi 404
def handler(app, event, context):
    return app(event, context)
