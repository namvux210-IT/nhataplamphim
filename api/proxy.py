from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
import functools

app = Flask(__name__)
CORS(app)

# Cache kết quả API trong bộ nhớ để Android TV tải nhanh hơn
@functools.lru_cache(maxsize=100)
def get_data(url):
    headers = {"accept": "application/json", "User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return response.json()
    except:
        return None

@app.route('/api/proxy')
def proxy_handler():
    kw = request.args.get('keyword', '')
    slug = request.args.get('path', '')
    
    # Sử dụng đúng mẫu URL tìm kiếm bạn cung cấp
    if slug:
        url = f"https://ophim1.com/v1/api/phim/{slug}"
    elif kw:
        url = f"https://ophim1.com/v1/api/tim-kiem?keyword={kw}"
    else:
        url = "https://ophim1.com/v1/api/danh-sach/phim-moi-cap-nhat?page=1"

    data = get_data(url)
    if not data:
        return jsonify({"status": False, "message": "API Ophim không phản hồi"})

    # FIX LỖI POSTER: Tự động thêm domain nếu thiếu
    img_domain = "https://img.phimapi.com/"
    
    if 'data' in data:
        # Nếu là danh sách phim (Tìm kiếm/Mới cập nhật)
        if 'items' in data['data']:
            for item in data['data']['items']:
                if item.get('poster_url') and not str(item['poster_url']).startswith('http'):
                    item['poster_url'] = f"{img_domain}{item['poster_url']}"
        # Nếu là chi tiết bộ phim
        if 'item' in data['data']:
            item = data['data']['item']
            if item.get('poster_url') and not str(item['poster_url']).startswith('http'):
                item['poster_url'] = f"{img_domain}{item['poster_url']}"

    return jsonify(data)
