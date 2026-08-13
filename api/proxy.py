"""
================================================================================
PROXY ĐA NGUỒN PHIM — KKPhim / NguonC / VSMOV
================================================================================
Mục tiêu: gọi tới 1 trong 3 nguồn API mã nguồn mở (hoặc cả 3 khi tìm kiếm),
CHUẨN HÓA dữ liệu trả về theo đúng khuôn dạng mà frontend cũ đã dùng
(kiểu Ophim/KKPhim: item.episodes[0].server_data[i].link_embed / link_m3u8),
để toàn bộ JS phía frontend không cần biết đang xem nguồn nào.

GHI CHÚ QUAN TRỌNG VỀ ĐỘ TIN CẬY DỮ LIỆU:
- KKPhim (phimapi.com): xác nhận trực tiếp từ tài liệu chính thức
  (kkphim.vip/help/help.html) — độ tin cậy CAO.
- NguonC (phim.nguonc.com): xác nhận trực tiếp từ tài liệu chính thức
  (ảnh chụp api-document do người dùng cung cấp) — TẤT CẢ URL endpoint +
  cấu trúc phong bì phản hồi (status/paginate/items) đã khớp 100% —
  độ tin cậy CAO cho URL. Chỉ riêng TÊN FIELD của từng phim
  (name/slug/thumb_url…) và cấu trúc "episodes" bên trong endpoint chi
  tiết KHÔNG được liệt kê rõ trong tài liệu, nên phần normalize vẫn được
  viết PHÒNG THỦ (thử nhiều tên field khả dĩ) để không vỡ trang.
  ĐÃ XÁC NHẬN QUA ?diag=1: NguonC trả 403 (chặn bởi WAF/bot-protection),
  trong khi KKPhim/VSMOV vẫn 200 OK bình thường -> đã thêm cơ chế
  warm_nguonc() (ghé trang chủ lấy cookie trước khi gọi API) để thử vượt
  qua. Nếu sau khi deploy bản này ?diag=1 vẫn báo 403 cho nguonc, nghĩa là
  WAF của họ dùng cơ chế chặn nâng cao hơn (JS challenge/Cloudflare
  Turnstile...) mà việc gọi API thuần server-to-server không thể vượt qua
  được — khi đó nên coi NguonC là nguồn không khả dụng để tích hợp, trang
  web vẫn hoạt động bình thường với 2 nguồn còn lại.
- VSMOV (vsmov.com/api): xác nhận cấu trúc endpoint từ trang
  vsmov.com/api-document — độ tin cậy CAO cho endpoint, TRUNG BÌNH cho
  tên field chi tiết (trang doc không hiển thị JSON mẫu đầy đủ do là tab JS).
  => Nếu chạy thử thấy nguồn nào thiếu ảnh/tên/tập phim, hãy gửi JSON mẫu
     (F12 > Network) để mình chỉnh nhanh hàm normalize tương ứng. Hoặc đơn
     giản hơn: mở thẳng ?debug=1 (ví dụ .../api/proxy?path=slug&source=
     nguonc&debug=1) để xem field "_raw" — chính là JSON gốc chưa chỉnh sửa
     mà nguồn trả về, khỏi cần mở DevTools.
  => Muốn kiểm tra NHANH cả 3 nguồn có đang "sống" không (bị chặn bot,
     sập, đổi domain...): mở .../api/proxy?diag=1 — trả về http_status,
     có parse được JSON không, và số phim lấy được của TỪNG nguồn trong
     1 lần gọi duy nhất.
  => Route /api/img?url=...&source=... : proxy ảnh qua server để gắn đúng
     Referer, dùng làm phương án dự phòng khi ảnh gốc bị chặn hotlink
     (xem imgFallback() trong index.html).

Deploy trên Vercel: file này export biến `app` (Flask, chuẩn WSGI) —
Vercel's Python runtime tự nhận diện và chạy được, xem vercel.json đi kèm.
================================================================================
"""
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor, as_completed

app = Flask(__name__)
CORS(app)

HEADERS_BASE = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}
REFERER = {
    "kkphim": "https://phimapi.com/",
    "nguonc": "https://phim.nguonc.com/",
    "vsmov": "https://vsmov.com/",
}
TIMEOUT = 12

# Session dùng lại kết nối (keep-alive) giữa các lần gọi trong cùng 1 lần
# khởi động serverless function -> phản hồi nhanh hơn. Có retry tự động
# (3 lần, backoff tăng dần) để vượt qua lỗi mạng/timeout tạm thời — đây là
# nguyên nhân phổ biến khiến 1 nguồn thỉnh thoảng trả về rỗng.
_session = requests.Session()
_retry = Retry(total=3, backoff_factor=0.4, status_forcelist=[429, 500, 502, 503, 504])
_session.mount("https://", HTTPAdapter(max_retries=_retry, pool_maxsize=20))
_session.mount("http://", HTTPAdapter(max_retries=_retry, pool_maxsize=20))

# ── "Làm nóng" phiên cho NguonC ──────────────────────────────────────────
# Diag đo được: NguonC trả 403 (WAF chặn thẳng) trong khi KKPhim/VSMOV vẫn
# 200 OK bình thường -> khả năng cao WAF của NguonC yêu cầu cookie phiên
# hợp lệ (được cấp khi ghé 1 trang HTML thường trước đó), request "lạ" gọi
# thẳng vào /api/... bị từ chối ngay. Khắc phục: ghé trang chủ 1 lần lấy
# cookie, dùng chung Session (giữ cookie) cho các lần gọi API kế tiếp
# trong cùng lượt khởi động serverless function.
_nguonc_warmed = False
_nguonc_warm_status = None


def warm_nguonc():
    global _nguonc_warmed, _nguonc_warm_status
    if _nguonc_warmed:
        return _nguonc_warm_status
    try:
        h = dict(HEADERS_BASE)
        h["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        r = _session.get("https://phim.nguonc.com/", headers=h, timeout=TIMEOUT)
        _nguonc_warm_status = r.status_code
    except Exception as e:
        _nguonc_warm_status = "error: " + str(e)[:100]
    _nguonc_warmed = True
    return _nguonc_warm_status



def get_json(url, source=None):
    if not url:
        return None
    if source == "nguonc":
        warm_nguonc()
    headers = dict(HEADERS_BASE)
    if source and REFERER.get(source):
        headers["Referer"] = REFERER[source]
    try:
        r = _session.get(url, headers=headers, timeout=TIMEOUT)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


# ═══════════════════════════════════════════════════════════════════════════
# CẤU HÌNH 3 NGUỒN
# ═══════════════════════════════════════════════════════════════════════════

KKPHIM_BASE = "https://phimapi.com"
NGUONC_BASE = "https://phim.nguonc.com/api"
VSMOV_BASE = "https://vsmov.com/api"

SOURCES = {
    "kkphim": {"name": "KKPhim", "base": KKPHIM_BASE},
    "nguonc": {"name": "Nguồn C", "base": NGUONC_BASE},
    "vsmov":  {"name": "VSMOV",   "base": VSMOV_BASE},
}

# Domain gốc dùng làm tiền tố dự phòng nếu API trả ảnh dạng đường dẫn tương
# đối (không có http/https ở đầu) — hiếm gặp nhưng vẫn phòng thủ cho chắc.
SITE_BASE = {
    "kkphim": "https://phimapi.com",
    "nguonc": "https://phim.nguonc.com",
    "vsmov":  "https://vsmov.com",
}


def fix_img(url, source):
    url = (url or "").strip()
    if not url:
        return ""
    if url.startswith("http://") or url.startswith("https://"):
        return url
    base = SITE_BASE.get(source, "")
    return base + ("" if url.startswith("/") else "/") + url

# type_list dùng cho các nút "Phim Lẻ / Phim Bộ / Hoạt Hình / TV Shows" — tên
# slug các nguồn không hoàn toàn giống nhau nên map riêng cho từng nguồn.
TYPE_LIST_MAP = {
    "kkphim": {"phim-le": "phim-le", "phim-bo": "phim-bo", "hoat-hinh": "hoat-hinh", "tv-shows": "tv-shows"},
    "vsmov":  {"phim-le": "phim-le", "phim-bo": "phim-bo", "hoat-hinh": "hoat-hinh", "tv-shows": "tv-shows"},
    "nguonc": {"phim-le": "phim-le", "phim-bo": "phim-bo", "hoat-hinh": "hoat-hinh", "tv-shows": "tv-shows"},
}


# ═══════════════════════════════════════════════════════════════════════════
# HÀM XÂY URL THEO TỪNG NGUỒN
# ═══════════════════════════════════════════════════════════════════════════

def url_home(source, page):
    if source == "kkphim":
        return f"{KKPHIM_BASE}/danh-sach/phim-moi-cap-nhat?page={page}"
    if source == "vsmov":
        return f"{VSMOV_BASE}/danh-sach/phim-moi-cap-nhat?page={page}"
    if source == "nguonc":
        return f"{NGUONC_BASE}/films/phim-moi-cap-nhat?page={page}"  # tài liệu chính thức: KHÔNG có "danh-sach/"


def url_type_list(source, type_list, page):
    slug = TYPE_LIST_MAP.get(source, {}).get(type_list, type_list)
    if source == "kkphim":
        return f"{KKPHIM_BASE}/v1/api/danh-sach/{slug}?page={page}"
    if source == "vsmov":
        return f"{VSMOV_BASE}/danh-sach/{slug}?page={page}"
    if source == "nguonc":
        return f"{NGUONC_BASE}/films/danh-sach/{slug}?page={page}"


def url_category(source, slug, page):
    if source == "kkphim":
        return f"{KKPHIM_BASE}/v1/api/the-loai/{slug}?page={page}"
    if source == "vsmov":
        return f"{VSMOV_BASE}/the-loai/{slug}?page={page}"
    if source == "nguonc":
        return f"{NGUONC_BASE}/films/the-loai/{slug}?page={page}"


def url_country(source, slug, page):
    if source == "kkphim":
        return f"{KKPHIM_BASE}/v1/api/quoc-gia/{slug}?page={page}"
    if source == "vsmov":
        return f"{VSMOV_BASE}/quoc-gia/{slug}?page={page}"
    if source == "nguonc":
        return f"{NGUONC_BASE}/films/quoc-gia/{slug}?page={page}"


def url_year(source, year, page):
    if source == "kkphim":
        return f"{KKPHIM_BASE}/v1/api/nam/{year}?page={page}"
    if source == "vsmov":
        return f"{VSMOV_BASE}/nam/{year}?page={page}"
    if source == "nguonc":
        return f"{NGUONC_BASE}/films/nam-phat-hanh/{year}?page={page}"  # xác nhận từ tài liệu chính thức


def url_search(source, keyword, page):
    if source == "kkphim":
        return f"{KKPHIM_BASE}/v1/api/tim-kiem?keyword={keyword}&page={page}&limit=24"
    if source == "vsmov":
        return f"{VSMOV_BASE}/tim-kiem?keyword={keyword}&limit=24"
    if source == "nguonc":
        return f"{NGUONC_BASE}/films/search?keyword={keyword}"  # tài liệu chính thức: không có tham số page


def url_detail(source, slug):
    if source == "kkphim":
        return f"{KKPHIM_BASE}/phim/{slug}"
    if source == "vsmov":
        return f"{VSMOV_BASE}/phim/{slug}"
    if source == "nguonc":
        return f"{NGUONC_BASE}/film/{slug}"


def url_cat_list(source):
    if source == "kkphim":
        return f"{KKPHIM_BASE}/the-loai"
    if source == "vsmov":
        return f"{VSMOV_BASE}/the-loai"
    return None  # NguonC: chưa xác nhận có endpoint danh sách thể loại riêng


def url_country_list(source):
    if source == "kkphim":
        return f"{KKPHIM_BASE}/quoc-gia"
    if source == "vsmov":
        return f"{VSMOV_BASE}/quoc-gia"
    return None


# ═══════════════════════════════════════════════════════════════════════════
# CHUẨN HÓA DỮ LIỆU
# ═══════════════════════════════════════════════════════════════════════════

def g(d, *keys, default=""):
    """Lấy giá trị đầu tiên khác rỗng trong danh sách key khả dĩ (phòng thủ)."""
    for k in keys:
        v = d.get(k)
        if v not in (None, ""):
            return v
    return default


def norm_item_ophim_like(raw, source):
    """KKPhim & VSMOV: schema đã gần giống Ophim gốc, gần như giữ nguyên."""
    return {
        "name": g(raw, "name"),
        "origin_name": g(raw, "origin_name", "original_name"),
        "slug": g(raw, "slug"),
        "thumb_url": fix_img(g(raw, "thumb_url"), source),
        "poster_url": fix_img(g(raw, "poster_url", default=g(raw, "thumb_url")), source),
        "year": g(raw, "year"),
        "quality": g(raw, "quality"),
        "lang": g(raw, "lang", "language"),
        "episode_current": g(raw, "episode_current", "current_episode"),
        "time": g(raw, "time"),
        "source": source,
    }


def norm_item_nguonc(raw):
    return {
        "name": g(raw, "name", "title"),
        "origin_name": g(raw, "origin_name", "original_name"),
        "slug": g(raw, "slug"),
        "thumb_url": fix_img(g(raw, "thumb_url"), "nguonc"),
        "poster_url": fix_img(g(raw, "poster_url", default=g(raw, "thumb_url")), "nguonc"),
        "year": g(raw, "publish_year", "year"),
        "quality": g(raw, "quality"),
        "lang": g(raw, "language", "lang"),
        "episode_current": g(raw, "current_episode", "total_episodes"),
        "time": g(raw, "time"),
        "source": "nguonc",
    }


def norm_list(raw, source):
    """Trả về list item đã chuẩn hoá, thử nhiều đường dẫn field khác nhau."""
    if not raw:
        return []
    items = None
    # Các khuôn dạng thường gặp: data.items / items / data.movies / movies
    if isinstance(raw.get("data"), dict) and isinstance(raw["data"].get("items"), list):
        items = raw["data"]["items"]
    elif isinstance(raw.get("items"), list):
        items = raw["items"]
    elif isinstance(raw.get("data"), dict) and isinstance(raw["data"].get("movies"), list):
        items = raw["data"]["movies"]
    if items is None:
        return []
    if source == "nguonc":
        return [norm_item_nguonc(it) for it in items]
    return [norm_item_ophim_like(it, source) for it in items]


def norm_categories(raw, source):
    """Danh sách [{name, slug}] cho menu Thể loại / Quốc gia."""
    if not raw:
        return []
    arr = raw if isinstance(raw, list) else raw.get("data") or []
    out = []
    for it in arr:
        if isinstance(it, dict) and it.get("slug"):
            out.append({"name": g(it, "name"), "slug": g(it, "slug")})
    return out


def parse_episodes_ophim_like(eps):
    """eps: list các nhóm server, ví dụ [{"server_name":..,"server_data":[...]}]"""
    out = []
    for sv in (eps or []):
        data = sv.get("server_data") or sv.get("items") or []
        out.append({
            "server_name": g(sv, "server_name", default="Server"),
            "server_data": [{
                "name": g(e, "name", default=g(e, "slug")),
                "slug": g(e, "slug"),
                "link_embed": g(e, "link_embed", "embed"),
                "link_m3u8": g(e, "link_m3u8", "m3u8"),
            } for e in data],
        })
    return out


def norm_detail(raw, source, slug):
    if not raw:
        return None

    if source in ("kkphim", "vsmov"):
        data_wrap = raw.get("data") or {}
        item = data_wrap.get("item") or raw.get("item") or raw.get("movie")
        if not item:
            return None
        item = dict(item)
        item.setdefault("source", source)
        # QUAN TRỌNG: "episodes" ở API kiểu KKPhim/VSMOV thường nằm NGANG HÀNG
        # với "movie" (raw["episodes"]), KHÔNG lồng bên trong "movie". Thử lần
        # lượt mọi vị trí khả dĩ để chắc chắn lấy được tập phim.
        eps_raw = (
            raw.get("episodes")
            or data_wrap.get("episodes")
            or item.get("episodes")
            or []
        )
        item["episodes"] = parse_episodes_ophim_like(eps_raw)
        item["thumb_url"] = fix_img(item.get("thumb_url"), source)
        item["poster_url"] = fix_img(item.get("poster_url") or item.get("thumb_url"), source)
        # category/country đã có sẵn dạng [{name,slug}] theo chuẩn Ophim
        item["category"] = item.get("category") or []
        item["country"] = item.get("country") or []
        item["actor"] = item.get("actor") or []
        item["director"] = item.get("director") or []
        return item

    if source == "nguonc":
        movie = raw.get("movie")
        if not movie:
            return None
        category, country = [], []
        cat_field = movie.get("category")
        if isinstance(cat_field, dict):
            for grp in cat_field.values():
                if not isinstance(grp, dict):
                    continue
                gname = (grp.get("group_name") or "").lower()
                lst = [{"name": g(x, "name"), "slug": g(x, "slug", "id")} for x in (grp.get("list") or [])]
                if "loại" in gname or "loai" in gname:
                    category = lst
                elif "gia" in gname or "quốc" in gname:
                    country = lst
        casts = movie.get("casts") or movie.get("actor") or ""
        actor = [a.strip() for a in casts.split(",")] if isinstance(casts, str) and casts else (casts if isinstance(casts, list) else [])
        director_raw = movie.get("director") or ""
        director = [d.strip() for d in director_raw.split(",")] if isinstance(director_raw, str) and director_raw else (director_raw if isinstance(director_raw, list) else [])

        episodes = []
        # Theo tài liệu, endpoint chi tiết chỉ trả field "movie" (không có field
        # rời ở cấp cao nhất) → episodes nhiều khả năng nằm TRONG movie.
        # Vẫn thử fallback ở cấp cao nhất phòng khi API có phiên bản khác.
        raw_eps = movie.get("episodes") or raw.get("episodes") or []
        for sv in raw_eps:
            items = sv.get("items") or sv.get("server_data") or []
            episodes.append({
                "server_name": g(sv, "server_name", default="Server"),
                "server_data": [{
                    "name": g(e, "name", default=g(e, "slug")),
                    "slug": g(e, "slug"),
                    "link_embed": g(e, "embed", "link_embed"),
                    "link_m3u8": g(e, "m3u8", "link_m3u8"),
                } for e in items],
            })

        return {
            "name": g(movie, "name"),
            "origin_name": g(movie, "original_name", "origin_name"),
            "slug": g(movie, "slug", default=slug),
            "content": g(movie, "description", "content"),
            "thumb_url": fix_img(g(movie, "thumb_url"), "nguonc"),
            "poster_url": fix_img(g(movie, "poster_url", default=g(movie, "thumb_url")), "nguonc"),
            "year": g(movie, "publish_year", "year"),
            "quality": g(movie, "quality"),
            "lang": g(movie, "language", "lang"),
            "episode_current": g(movie, "current_episode"),
            "time": g(movie, "time"),
            "actor": actor,
            "director": director,
            "category": category,
            "country": country,
            "episodes": episodes,
            "source": "nguonc",
        }

    return None


# ═══════════════════════════════════════════════════════════════════════════
# ROUTE CHÍNH
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/api/img")
def img_proxy():
    """
    Proxy ảnh poster qua server để gắn đúng header Referer/User-Agent của
    nguồn gốc. Nguyên nhân phổ biến khiến MỘT SỐ ảnh (thường là KKPhim)
    không hiển thị: CDN ảnh bật chống hotlink, chỉ chấp nhận request có
    Referer trỏ về đúng domain của họ — mà khi <img> tải trực tiếp từ trang
    web của bạn, trình duyệt gửi Referer là domain CỦA BẠN nên bị chặn.
    Frontend chỉ gọi route này làm phương án DỰ PHÒNG khi ảnh gốc lỗi
    (xem hàm imgFallback trong index.html) — ảnh tải trực tiếp vẫn được ưu
    tiên trước để giữ tốc độ nhanh nhất.
    """
    url = request.args.get("url", "").strip()
    source = request.args.get("source", "kkphim").strip()
    if not url or not url.startswith(("http://", "https://")):
        return Response(status=400)
    if source == "nguonc":
        warm_nguonc()
    headers = dict(HEADERS_BASE)
    headers["Accept"] = "image/webp,image/avif,image/*,*/*;q=0.8"
    if REFERER.get(source):
        headers["Referer"] = REFERER[source]
    try:
        r = _session.get(url, headers=headers, timeout=TIMEOUT, stream=True)
        if r.status_code != 200:
            return Response(status=502)
        return Response(
            r.content,
            content_type=r.headers.get("Content-Type", "image/jpeg"),
            headers={"Cache-Control": "public, max-age=86400"},
        )
    except Exception:
        return Response(status=502)


@app.route("/api/proxy")
def handle():
    source = (request.args.get("source") or "kkphim").strip()
    slug = request.args.get("path", "").strip()
    kw = request.args.get("keyword", "").strip()
    cat = request.args.get("cat", "").strip()
    nation = request.args.get("nation", "").strip()
    year = request.args.get("year", "").strip()
    type_list = request.args.get("type", "").strip()
    list_meta = request.args.get("list", "").strip()  # 'the-loai' | 'quoc-gia'
    page = request.args.get("page", "1").strip()
    debug = request.args.get("debug") == "1"

    # ── Chẩn đoán nhanh: kiểm tra tình trạng cả 3 nguồn cùng lúc ──
    # Mở /api/proxy?diag=1 để xem status code + số phim lấy được của từng nguồn.
    if request.args.get("diag") == "1":
        result = {}
        for s in SOURCES:
            info = {"url": url_home(s, "1")}
            if s == "nguonc":
                info["homepage_status"] = warm_nguonc()
            try:
                headers = dict(HEADERS_BASE)
                if REFERER.get(s):
                    headers["Referer"] = REFERER[s]
                r = _session.get(info["url"], headers=headers, timeout=TIMEOUT)
                info["http_status"] = r.status_code
                # Lấy các header hay dùng để nhận diện WAF/CDN đang chặn
                # (Cloudflare, Sucuri, Nginx tùy biến...) — giúp biết chính
                # xác cần vượt qua cơ chế nào.
                waf_headers = {}
                for hk in ["server", "cf-ray", "cf-mitigated", "x-sucuri-id",
                           "x-waf-event-info", "content-type", "content-encoding"]:
                    if hk in r.headers:
                        waf_headers[hk] = r.headers[hk]
                info["response_headers"] = waf_headers
                try:
                    j = r.json()
                    info["json_ok"] = True
                    info["items_found"] = len(norm_list(j, s))
                except Exception as pe:
                    info["json_ok"] = False
                    info["items_found"] = 0
                    info["parse_error"] = str(pe)
                    info["body_preview"] = r.text[:300]
            except requests.exceptions.Timeout:
                info["error"] = "TIMEOUT sau " + str(TIMEOUT) + "s — nguồn phản hồi quá chậm hoặc chặn request."
            except requests.exceptions.ConnectionError as ce:
                info["error"] = "CONNECTION_ERROR — " + str(ce)[:200]
            except Exception as e:
                info["error"] = str(e)[:200]
            result[s] = info
        return jsonify({"status": True, "diag": result})

    # ── Danh sách thể loại / quốc gia (để dựng menu động) ──
    if list_meta:
        if list_meta == "the-loai":
            raw = get_json(url_cat_list(source), source) if url_cat_list(source) else None
        elif list_meta == "quoc-gia":
            raw = get_json(url_country_list(source), source) if url_country_list(source) else None
        else:
            raw = None
        return jsonify({"status": True, "source": source, "data": {"items": norm_categories(raw, source)}})

    # ── Chi tiết phim ──
    if slug:
        raw = get_json(url_detail(source, slug), source)
        item = norm_detail(raw, source, slug)
        if not item:
            resp = {"status": False, "source": source}
            if debug:
                resp["_raw"] = raw
            return jsonify(resp)
        resp = {"status": True, "source": source, "data": {"item": item}}
        if debug:
            resp["_raw"] = raw
        r = jsonify(resp)
        r.headers["Cache-Control"] = "public, max-age=60"
        return r

    # ── Tìm kiếm: source=all -> tìm song song cả 3 nguồn ──
    if kw:
        if source == "all":
            items = []
            with ThreadPoolExecutor(max_workers=3) as ex:
                futs = {ex.submit(get_json, url_search(s, kw, page), s): s for s in SOURCES}
                for fut in as_completed(futs):
                    s = futs[fut]
                    try:
                        raw = fut.result()
                        items.extend(norm_list(raw, s))
                    except Exception:
                        continue
            return jsonify({"status": True, "source": "all", "data": {"items": items}})
        raw = get_json(url_search(source, kw, page), source)
        return jsonify({"status": True, "source": source, "data": {"items": norm_list(raw, source)}})

    # ── Danh sách theo bộ lọc ──
    if cat:
        raw = get_json(url_category(source, cat, page), source)
    elif nation:
        raw = get_json(url_country(source, nation, page), source)
    elif year:
        raw = get_json(url_year(source, year, page), source)
    elif type_list:
        raw = get_json(url_type_list(source, type_list, page), source)
    else:
        raw = get_json(url_home(source, page), source)

    resp = {"status": True, "source": source, "data": {"items": norm_list(raw, source)}}
    if debug:
        resp["_raw"] = raw
    return jsonify(resp)


if __name__ == "__main__":
    app.run(port=5000, debug=True)
