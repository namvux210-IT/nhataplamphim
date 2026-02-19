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
    slug = request.args.get('path', '').strip()
    kw = request.args.get('keyword', '').strip()

    if slug:
        data = get_ophim_data(f"https://ophim1.com/v1/api/phim/{slug}")
        if data and 'data' in data:
            # Sửa lỗi IMAGE ERROR bằng cách lấy poster chuẩn
            img_res = get_ophim_data(f"https://ophim1.com/v1/api/phim/{slug}/images")
            if img_res and img_res.get('status'):
                data['data']['item']['poster_url'] = img_res['data'].get('og_image') or img_res['data'].get('poster_url')
        return jsonify(data or {"status": False})

    # Xử lý tìm kiếm hoặc danh sách mới nhất
    url = f"https://ophim1.com/v1/api/tim-kiem?keyword={kw}" if kw else "https://ophim1.com/v1/api/danh-sach/phim-moi-cap-nhat?page=1"
    data = get_ophim_data(url)
    if data and 'data' in data and 'items' in data['data']:
        for i in data['data']['items']:
            p = i.get('poster_url') or i.get('thumb_url')
            if p and not str(p).startswith('http'):
                i['poster_url'] = f"https://img.phimapi.com/{p}"
    return jsonify(data or {"status": False})
