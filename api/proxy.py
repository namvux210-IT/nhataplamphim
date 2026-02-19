from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_ophim_data(url):
    headers = {"accept": "application/json", "User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        return r.json() if r.status_code == 200 else None
    except:
        return None

@app.route('/api/proxy')
def handle():
    # Lấy và làm sạch tham số đầu vào
    slug = request.args.get('path', '').strip()
    kw = request.args.get('keyword', '').strip()
    cat = request.args.get('category', '').strip()

    # TRƯỜNG HỢP 1: LẤY CHI TIẾT PHIM (Dùng slug)
    if slug:
        data = get_ophim_data(f"https://ophim1.com/v1/api/phim/{slug}")
        if data and 'data' in data:
            # Sửa lỗi poster: Gọi endpoint chuyên dụng
            img_res = get_ophim_data(f"https://ophim1.com/v1/api/phim/{slug}/images")
            if img_res and img_res.get('status'):
                img_info = img_res.get('data', {})
                # Ưu tiên lấy og_image vì nó thường chứa link đầy đủ
                data['data']['item']['poster_url'] = img_info.get('og_image') or img_info.get('poster_url')
        return jsonify(data or {"status": False})

    # TRƯỜNG HỢP 2: LẤY DANH SÁCH (Trang chủ / Tìm kiếm / Thể loại)
    if kw:
        url = f"https://ophim1.com/v1/api/tim-kiem?keyword={kw}"
    elif cat:
        url = f"https://ophim1.com/v1/api/the-loai/{cat}"
    else:
        url = "https://ophim1.com/v1/api/danh-sach/phim-moi-cap-nhat?page=1"

    data = get_ophim_data(url)
    if data and 'data' in data and 'items' in data['data']:
        domain = "https://img.phimapi.com/"
        for i in data['data']['items']:
            # Sửa lỗi domain poster cho danh sách ngoài trang chủ
            p = i.get('poster_url') or i.get('thumb_url')
            if p and not str(p).startswith('http'):
                i['poster_url'] = f"{domain}{p}"
                
    return jsonify(data or {"status": False})
