from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Cache đơn giản để tăng tốc Android TV
cache = {}

@app.route('/api/proxy')
def handle():
    path = request.args.get('path', '')
    kw = request.args.get('keyword', '')
    
    # Xây dựng URL dựa trên hành động (Chi tiết hoặc Tìm kiếm)
    if path:
        url = f"https://ophim1.com/api/v1/phim/{path}"
    else:
        url = f"https://ophim1.com/api/v1/tim-kiem?keyword={kw}"

    if url in cache: return jsonify(cache[url])

    try:
        headers = {"accept": "application/json", "User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=10).json()
        
        # Sửa lỗi Poster không hiển thị: Tự động ghép domain nếu thiếu
        def fix_img(item):
            if 'poster_url' in item and item['poster_url'] and not item['poster_url'].startswith('http'):
                item['poster_url'] = f"https://img.phimapi.com/{item['poster_url']}"
            if 'thumb_url' in item and item['thumb_url'] and not item['thumb_url'].startswith('http'):
                item['thumb_url'] = f"https://img.phimapi.com/{item['thumb_url']}"
            return item

        if 'data' in resp:
            if 'items' in resp['data']: # Danh sách tìm kiếm
                resp['data']['items'] = [fix_img(i) for i in resp['data']['items']]
            if 'item' in resp['data']: # Chi tiết phim
                resp['data']['item'] = fix_img(resp['data']['item'])
        
        cache[url] = resp
        return jsonify(resp)
    except:
        return jsonify({"status": False, "message": "API Error"})
