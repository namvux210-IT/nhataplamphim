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

    if genres: url = "https://ophim1.com/v1/api/the-loai"
    elif cat: url = f"https://ophim1.com/v1/api/the-loai/{cat}"
    elif slug: url = f"https://ophim1.com/v1/api/phim/{slug}"
    elif kw: url = f"https://ophim1.com/v1/api/tim-kiem?keyword={kw}"
    else: url = "https://ophim1.com/v1/api/danh-sach/phim-moi-cap-nhat?page=1"

    data = get_ophim_data(url)
    if not data: return jsonify({"status": False})

    # FIX LỖI POSTER TRIỆT ĐỂ
    domain = "https://img.phimapi.com/"
    def fix_url(url_str):
        if not url_str: return ""
        if str(url_str).startswith('http'): return url_str
        return f"{domain}{url_str}"

    if 'data' in data:
        items = data['data'].get('items', [])
        item = data['data'].get('item')
        if items:
            for i in items:
                i['poster_url'] = fix_url(i.get('poster_url') or i.get('thumb_url'))
        if item:
            item['poster_url'] = fix_url(item.get('poster_url') or item.get('thumb_url'))
                
    return jsonify(data)
