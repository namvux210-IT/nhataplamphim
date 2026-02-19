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
    genres = request.args.get('genres', '') # Lấy danh sách thể loại

    # Phân loại URL theo đúng yêu cầu của bạn
    if genres:
        url = "https://ophim1.com/v1/api/the-loai"
    elif cat:
        url = f"https://ophim1.com/v1/api/the-loai/{cat}"
    elif slug:
        url = f"https://ophim1.com/v1/api/phim/{slug}"
    elif kw:
        url = f"https://ophim1.com/v1/api/tim-kiem?keyword={kw}"
    else:
        url = "https://ophim1.com/v1/api/danh-sach/phim-moi-cap-nhat?page=1"

    data = get_ophim_data(url)
    if not data: return jsonify({"status": False})

    # Fix lỗi Poster thiếu domain
    domain = "https://img.phimapi.com/"
    if 'data' in data:
        items = data['data'].get('items', [])
        item = data['data'].get('item')
        
        if items:
            for i in items:
                if i.get('poster_url') and not str(i['poster_url']).startswith('http'):
                    i['poster_url'] = f"{domain}{i['poster_url']}"
        if item:
            if item.get('poster_url') and not str(item['poster_url']).startswith('http'):
                item['poster_url'] = f"{domain}{item['poster_url']}"
                
    return jsonify(data)
