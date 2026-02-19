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
    cat = request.args.get('category', '').strip()

    # CHI TIẾT PHIM + LẤY ẢNH CHUẨN
    if slug:
        movie_data = get_ophim_data(f"https://ophim1.com/v1/api/phim/{slug}")
        if movie_data and 'data' in movie_data:
            # Gọi endpoint images bạn cung cấp
            img_res = get_ophim_data(f"https://ophim1.com/v1/api/phim/{slug}/images")
            if img_res and img_res.get('status'):
                img_info = img_res.get('data', {})
                # Gán ảnh chuẩn có sẵn domain
                movie_data['data']['item']['poster_url'] = img_info.get('og_image') or img_info.get('poster_url')
        return jsonify(movie_data or {"status": False})

    # DANH SÁCH PHIM
    if kw: url = f"https://ophim1.com/v1/api/tim-kiem?keyword={kw}"
    elif cat: url = f"https://ophim1.com/v1/api/the-loai/{cat}"
    else: url = "https://ophim1.com/v1/api/danh-sach/phim-moi-cap-nhat?page=1"

    data = get_ophim_data(url)
    if data and 'data' in data and 'items' in data['data']:
        domain = "https://img.phimapi.com/"
        for i in data['data']['items']:
            p = i.get('poster_url') or i.get('thumb_url')
            if p and not str(p).startswith('http'):
                i['poster_url'] = f"{domain}{p}"
                
    return jsonify(data or {"status": False})
