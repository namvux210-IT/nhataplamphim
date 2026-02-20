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
    cat = request.args.get('cat', '').strip() # Thể loại
    nation = request.args.get('nation', '').strip() # Quốc gia
    
    if slug:
        data = get_data(f"https://ophim1.com/v1/api/phim/{slug}")
        if data and 'data' in data:
            item = data['data']['item']
            for field in ['poster_url', 'thumb_url']:
                if item.get(field) and not item[field].startswith('http'):
                    item[field] = f"{CDN_URL}/{item[field]}"
        return jsonify(data or {"status": False})

    # Cấu trúc URL linh hoạt theo tài liệu ophim17.cc
    if kw:
        url = f"https://ophim1.com/v1/api/tim-kiem?keyword={kw}"
    elif cat:
        url = f"https://ophim1.com/v1/api/the-loai/{cat}?page=1"
    elif nation:
        url = f"https://ophim1.com/v1/api/quoc-gia/{nation}?page=1"
    else:
        url = "https://ophim1.com/v1/api/danh-sach/phim-moi-cap-nhat?page=1"

    data = get_data(url)
    if data and 'data' in data and 'items' in data['data']:
        for i in data['data']['items']:
            for field in ['poster_url', 'thumb_url']:
                if i.get(field) and not str(i[field]).startswith('http'):
                    i[field] = f"{CDN_URL}/{i[field]}"
    return jsonify(data or {"status": False})
