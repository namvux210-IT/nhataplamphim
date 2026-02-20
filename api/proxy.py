from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_data(url):
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        return r.json() if r.status_code == 200 else None
    except: return None

@app.route('/api/proxy')
def handle():
    slug = request.args.get('path', '').strip()
    kw = request.args.get('keyword', '').strip()
    
    # 1. Lấy chi tiết phim & Thông tin tập phim
    if slug:
        data = get_data(f"https://ophim1.com/v1/api/phim/{slug}")
        if data and 'data' in data:
            item = data['data']['item']
            # Kiểm tra và gắn domain ảnh chuẩn nếu thiếu
            if item.get('poster_url') and not item['poster_url'].startswith('http'):
                item['poster_url'] = f"https://img.phimapi.com/{item['poster_url']}"
        return jsonify(data or {"status": False})

    # 2. Lấy danh sách phim / Tìm kiếm
    url = f"https://ophim1.com/v1/api/tim-kiem?keyword={kw}" if kw else "https://ophim1.com/v1/api/danh-sach/phim-moi-cap-nhat?page=1"
    data = get_data(url)
    if data and 'data' in data and 'items' in data['data']:
        for i in data['data']['items']:
            # Gắn domain ảnh cho danh sách ngoài trang chủ
            p = i.get('poster_url') or i.get('thumb_url')
            if p and not str(p).startswith('http'):
                i['poster_url'] = f"https://img.phimapi.com/{p}"
    return jsonify(data or {"status": False})
