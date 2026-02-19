from flask import Flask, request, jsonify, make_response
import requests
from flask_cors import CORS
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
CORS(app)

# Cấu hình nguồn API
SOURCES = {
    "ophim": "https://ophim1.com/api/v1",
    "kkphim": "https://phimapi.com",
    "nguonc": "https://phim.nguonc.com/api"
}

def fetch_source(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        resp = requests.get(url, headers=headers, timeout=5)
        return resp.json()
    except:
        return None

@app.route('/api/movies')
def get_movies():
    keyword = request.args.get('keyword', '')
    page = request.args.get('page', '1')
    path = request.args.get('path', '')
    src = request.args.get('src', '')

    # 1. Nếu là yêu cầu lấy CHI TIẾT 1 bộ phim
    if path and src:
        base = SOURCES.get(src)
        # Chuẩn hóa endpoint theo tài liệu
        if src == "nguonc": url = f"{base}/film/{path}"
        elif src == "kkphim": url = f"{base}/phim/{path}"
        else: url = f"{base}/phim/{path}"
        return jsonify(fetch_source(url))

    # 2. Nếu là TÌM KIẾM hoặc TRANG CHỦ (Merge 3 nguồn)
    urls = []
    if keyword:
        urls = [
            (f"{SOURCES['ophim']}/tim-kiem?keyword={keyword}&page={page}", "ophim"),
            (f"{SOURCES['kkphim']}/v1/api/tim-kiem?keyword={keyword}&page={page}", "kkphim"),
            (f"{SOURCES['nguonc']}/films/search?keyword={keyword}&page={page}", "nguonc")
        ]
    else:
        urls = [
            (f"{SOURCES['ophim']}/danh-sach/phim-moi-cap-nhat?page={page}", "ophim"),
            (f"{SOURCES['kkphim']}/danh-sach/phim-moi-cap-nhat?page={page}", "kkphim"),
            (f"{SOURCES['nguonc']}/films/phim-moi-cap-nhat?page={page}", "nguonc")
        ]

    with ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(lambda x: (fetch_source(x[0]), x[1]), urls))

    merged_data = []
    for data, name in results:
        if not data: continue
        items = data.get('data', {}).get('items', []) if name != "nguonc" else data.get('items', [])
        for item in items:
            item['_source'] = name # Đánh dấu nguồn phim
            merged_data.append(item)

    return jsonify(merged_data)

if __name__ == '__main__':
    app.run(debug=True)
