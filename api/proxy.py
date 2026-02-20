from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

CDN_URL = "https://img.ophim.live/uploads/movies"
BASE_URL = "https://ophim1.com/v1/api"

def get_data(url):
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        return r.json() if r.status_code == 200 else None
    except: return None

@app.route('/api/proxy')
def handle():
    slug = request.args.get('path', '').strip()
    kw = request.args.get('keyword', '').strip()
    cat = request.args.get('cat', '').strip()     # Thể loại
    nat = request.args.get('nation', '').strip()  # Quốc gia
    year = request.args.get('year', '').strip()   # Năm
    
    # 1. Chi tiết phim (Giữ nguyên lõi cũ để không lỗi)
    if slug:
        data = get_data(f"{BASE_URL}/phim/{slug}")
        if data and 'data' in data:
            item = data['data']['item']
            if item.get('poster_url') and not item['poster_url'].startswith('http'):
                item['poster_url'] = f"{CDN_URL}/{item['poster_url']}"
            if item.get('thumb_url') and not item['thumb_url'].startswith('http'):
                item['thumb_url'] = f"{CDN_URL}/{item['thumb_url']}"
        return jsonify(data or {"status": False})

    # 2. Xử lý danh sách phim theo phân loại chuẩn Document
    # Mặc định là phim mới cập nhật
    url = f"{BASE_URL}/danh-sach/phim-moi-cap-nhat?page=1"
    
    if kw: # Tìm kiếm
        url = f"{BASE_URL}/tim-kiem?keyword={kw}"
    elif cat: # Theo thể loại: /the-loai/{slug}
        url = f"{BASE_URL}/the-loai/{cat}?page=1"
    elif nat: # Theo quốc gia: /quoc-gia/{slug}
        url = f"{BASE_URL}/quoc-gia/{nat}?page=1"
    elif year: # Theo năm: /danh-sach/phim-moi?year={year}
        url = f"{BASE_URL}/danh-sach/phim-moi?year={year}&page=1"

    data = get_data(url)
    
    # Chuẩn hóa URL ảnh cho tất cả danh sách để hiện poster
    if data and 'data' in data and 'items' in data['data']:
        for i in data['data']['items']:
            for key in ['poster_url', 'thumb_url']:
                val = i.get(key)
                if val and not val.startswith('http'):
                    i[key] = f"{CDN_URL}/{val}"
                    
    return jsonify(data or {"status": False})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
