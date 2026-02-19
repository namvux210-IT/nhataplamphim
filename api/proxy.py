from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)

# Bộ nhớ đệm (Cache) đơn giản trong RAM
# Trong môi trường thực tế, kết quả sẽ được lưu để tránh gọi API Ophim liên tục
cache_store = {}
CACHE_TIME = 600 # Cache trong 10 phút

@app.route('/api/proxy')
def handle():
    kw = request.args.get('keyword', '')
    slug = request.args.get('path', '')
    
    # Tạo URL dựa trên yêu cầu: Tìm kiếm hoặc Chi tiết phim
    if slug:
        target_url = f"https://ophim1.com/v1/api/phim/{slug}"
    else:
        # Sử dụng đúng mẫu URL bạn cung cấp
        target_url = f"https://ophim1.com/v1/api/tim-kiem?keyword={kw}"

    # Kiểm tra Cache
    current_time = time.time()
    if target_url in cache_store:
        entry = cache_store[target_url]
        if current_time - entry['timestamp'] < CACHE_TIME:
            return jsonify(entry['data'])

    # Thực hiện gọi API bằng requests theo mẫu bạn cung cấp
    headers = {"accept": "application/json", "User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(target_url, headers=headers, timeout=10)
        data = response.json()

        # Logic sửa lỗi Poster: Tự động ghép domain nếu path bị thiếu
        domain = "https://img.phimapi.com/"
        
        if 'data' in data:
            # Nếu là danh sách tìm kiếm
            if 'items' in data['data']:
                for item in data['data']['items']:
                    if item.get('poster_url') and not item['poster_url'].startswith('http'):
                        item['poster_url'] = f"{domain}{item['poster_url']}"
            # Nếu là chi tiết 1 bộ phim
            if 'item' in data['data']:
                item = data['data']['item']
                if item.get('poster_url') and not item['poster_url'].startswith('http'):
                    item['poster_url'] = f"{domain}{item['poster_url']}"

        # Lưu vào cache trước khi trả về
        cache_store[target_url] = {'data': data, 'timestamp': current_time}
        return jsonify(data)
    except Exception as e:
        return jsonify({"status": False, "error": str(e)})
