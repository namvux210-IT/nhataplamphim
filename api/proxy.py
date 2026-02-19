from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
import functools

app = Flask(__name__)
CORS(app)

@functools.lru_cache(maxsize=128)
def get_ophim_data(url):
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
    cat = request.args.get('category', '')
    genres = request.args.get('genres', '')

    # 1. Định nghĩa URL chính
    if genres: url = "https://ophim1.com/v1/api/the-loai"
    elif cat: url = f"https://ophim1.com/v1/api/the-loai/{cat}"
    elif slug: url = f"https://ophim1.com/v1/api/phim/{slug}"
    elif kw: url = f"https://ophim1.com/v1/api/tim-kiem?keyword={kw}"
    else: url = "https://ophim1.com/v1/api/danh-sach/phim-moi-cap-nhat?page=1"

    data = get_ophim_data(url)
    if not data: return jsonify({"status": False})

    # 2. Xử lý ảnh bằng endpoint /images nếu là chi tiết phim [Sửa lỗi poster]
    if slug and 'data' in data:
        img_url = f"https://ophim1.com/v1/api/phim/{slug}/images"
        img_data = get_ophim_data(img_url)
        if img_data and img_data.get('status'):
            # Ưu tiên lấy ảnh từ endpoint images chuyên dụng
            data['data']['item']['poster_url'] = img_data['data'].get('poster_url')
            data['data']['item']['thumb_url'] = img_data['data'].get('thumb_url')

    # 3. Fix domain ảnh dự phòng cho danh sách ngoài trang chủ
    domain = "https://img.phimapi.com/"
    if 'data' in data:
        items = data['data'].get('items', [])
        for i in items:
            if i.get('poster_url') and not str(i['poster_url']).startswith('http'):
                i['poster_url'] = f"{domain}{i['poster_url']}"
                
    return jsonify(data)
