from flask import Flask, request, jsonify, make_response
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/proxy')
def proxy():
    path = request.args.get('path', 'danh-sach/phim-moi-cap-nhat')
    # Loại bỏ dấu / ở đầu nếu có để tránh lỗi chuỗi
    target_path = path.lstrip('/')
    target_url = f"https://ophim1.com/api/v1/{target_path}"
    
    try:
        response = requests.get(target_url, timeout=10)
        # Kiểm tra nếu API OPhim trả về lỗi
        response.raise_for_status()
        data = response.json()
        
        res = make_response(jsonify(data))
        # Cache 1 giờ để tránh quá tải
        res.headers['Cache-Control'] = 's-maxage=3600, stale-while-revalidate=600'
        return res
    except Exception as e:
        # Nếu lỗi, trả về chi tiết để debug
        return jsonify({"error": str(e)}), 500

# Chỉ dùng để chạy local, Vercel sẽ bỏ qua dòng này
if __name__ == '__main__':
    app.run()
