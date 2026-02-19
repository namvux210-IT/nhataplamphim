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
    slug = request.args.get('path', '')
    kw = request.args.get('keyword', '')
    cat = request.args.get('category', '')
    genres = request.args.get('genres', '')

    # Định hướng API dựa trên yêu cầu từ giao diện
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

    # XỬ LÝ ẢNH TRUYỀN VỀ (Fix lỗi Poster)
    domain = "https://img.phimapi.com/"
    
    # Nếu là chi tiết 1 bộ phim: Gọi thêm endpoint /images để lấy link chuẩn
    if slug and 'data' in data and 'item' in data['data']:
        img_res = get_ophim_data(f"https://ophim1.com/v1/api/phim/{slug}/images")
        if img_res and img_res.get('status'):
            img_info = img_res.get('data', {})
            # Ưu tiên og_image vì thường có sẵn domain đầy đủ
            data['data']['item']['poster_url'] = img_info.get('og_image') or img_info.get('poster_url')

    # Fix domain cho danh sách phim ngoài trang chủ
    if 'data' in data and 'items' in data['data']:
        for i in data['data']['items']:
            if i.get('poster_url') and not str(i['poster_url']).startswith('http'):
                i['poster_url'] = f"{domain}{i['poster_url']}"
                
    return jsonify(data)
