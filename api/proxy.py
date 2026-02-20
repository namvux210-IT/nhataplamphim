from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

CDN_URL = "https://img.ophim.live/uploads/movies"

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
            item = data['data']['item']
            if item.get('poster_url') and not item['poster_url'].startswith('http'):
                item['poster_url'] = f"{CDN_URL}/{item['poster_url']}"
            if item.get('thumb_url') and not item['thumb_url'].startswith('http'):
                item['thumb_url'] = f"{CDN_URL}/{item['thumb_url']}"
        return jsonify(data or {"status": False})

    # Xử lý tìm kiếm hoặc danh sách phim mới
    url = f"https://ophim1.com/v1/api/tim-kiem?keyword={kw}" if kw else "https://ophim1.com/v1/api/danh-sach/phim-moi-cap-nhat?page=1"
    data = get_data(url)
    if data and 'data' in data and 'items' in data['data']:
        for i in data['data']['items']:
            p = i.get('poster_url') or i.get('thumb_url')
            if i.get('poster_url') and not str(i['poster_url']).startswith('http'):
                i['poster_url'] = f"{CDN_URL}/{i['poster_url']}"
            if i.get('thumb_url') and not str(i['thumb_url']).startswith('http'):
                i['thumb_url'] = f"{CDN_URL}/{i['thumb_url']}"
    return jsonify(data or {"status": False})

if __name__ == '__main__':
    app.run(debug=True)
