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

    if slug:
        data = get_data(f"https://ophim1.com/v1/api/phim/{slug}")
        if data and 'data' in data:
            # Lấy poster chuẩn TMDB để không bị lỗi ảnh
            img_res = get_data(f"https://ophim1.com/v1/api/phim/{slug}/images")
            if img_res and img_res.get('status'):
                data['data']['item']['poster_url'] = img_res['data'].get('og_image')
        return jsonify(data or {"status": False})

    url = f"https://ophim1.com/v1/api/tim-kiem?keyword={kw}" if kw else "https://ophim1.com/v1/api/danh-sach/phim-moi-cap-nhat?page=1"
    data = get_data(url)
    if data and 'data' in data and 'items' in data['data']:
        for i in data['data']['items']:
            if i.get('poster_url') and not str(i['poster_url']).startswith('http'):
                i['poster_url'] = f"https://img.phimapi.com/{i['poster_url']}"
    return jsonify(data or {"status": False})
