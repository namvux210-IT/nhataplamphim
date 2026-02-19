from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
import functools

app = Flask(__name__)
CORS(app)

# Cache đơn giản để tăng tốc độ phản hồi
@functools.lru_cache(maxsize=128)
def fetch_from_ophim(url):
    headers = {"accept": "application/json", "User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        return r.json()
    except:
        return None

@app.route('/api/proxy')
def handle():
    kw = request.args.get('keyword', '')
    slug = request.args.get('path', '')
    
    # Khớp chính xác với code mẫu bạn gửi
    if slug:
        url = f"https://ophim1.com/v1/api/phim/{slug}"
    elif kw:
        url = f"https://ophim1.com/v1/api/tim-kiem?keyword={kw}"
    else:
        url = "https://ophim1.com/v1/api/danh-sach/phim-moi-cap-nhat?page=1"

    data = fetch_from_ophim(url)
    if not data:
        return jsonify({"status": False, "msg": "Server Ophim không phản hồi"})

    # Sửa lỗi Poster không hiển thị (No Poster)
    # Tự động thêm domain nếu Ophim chỉ trả về path tương đối
    def fix_assets(obj):
        domain = "https://img.phimapi.com/"
        for key in ['poster_url', 'thumb_url']:
            if key in obj and obj[key] and not str(obj[key]).startswith('http'):
                obj[key] = f"{domain}{obj[key]}"
        return obj

    # Xử lý bóc tách dựa trên cấu trúc JSON thực tế của Ophim
    if 'data' in data:
        if 'items' in data['data']: # Danh sách phim
            data['data']['items'] = [fix_assets(item) for item in data['data']['items']]
        if 'item' in data['data']: # Chi tiết 1 bộ phim
            data['data']['item'] = fix_assets(data['data']['item'])
            
    return jsonify(data)
