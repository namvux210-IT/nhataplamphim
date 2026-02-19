from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_ophim_data(url):
    headers = {"accept": "application/json", "User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            return r.json()
        return None
    except Exception:
        return None

@app.route('/api/proxy')
def handle():
    # Làm sạch tham số đầu vào để tránh lỗi 404
    slug = request.args.get('path', '').strip()
    kw = request.args.get('keyword', '').strip()
    cat = request.args.get('category', '').strip()

    # ƯU TIÊN 1: LẤY CHI TIẾT PHIM (Khi có slug)
    if slug:
        data = get_ophim_data(f"https://ophim1.com/v1/api/phim/{slug}")
        if data and 'data' in data:
            # Tích hợp endpoint lấy ảnh chuẩn
            img_res = get_ophim_data(f"https://ophim1.com/v1/api/phim/{slug}/images")
            if img_res and img_res.get('status'):
                img_info = img_res.get('data', {})
                # Gán og_image vì nó là link full domain
                data['data']['item']['poster_url'] = img_info.get('og_image') or img_info.get('poster_url')
        return jsonify(data or {"status": False, "msg": "Movie not found"})

    # ƯU TIÊN 2: LẤY DANH SÁCH (Tìm kiếm hoặc Thể loại)
    if kw:
        url = f"https://ophim1.com/v1/api/tim-kiem?keyword={kw}"
    elif cat:
        url = f"https://ophim1.com/v1/api/the-loai/{cat}"
    else:
        url = "https://ophim1.com/v1/api/danh-sach/phim-moi-cap-nhat?page=1"

    data = get_ophim_data(url)
    # Tự động thêm domain cho poster trong danh sách
    if data and 'data' in data and 'items' in data['data']:
        domain = "https://img.phimapi.com/"
        for i in data['data']['items']:
            p = i.get('poster_url') or i.get('thumb_url')
            if p and not str(p).startswith('http'):
                i['poster_url'] = f"{domain}{p}"
                
    return jsonify(data or {"status": False, "msg": "API connection error"})
