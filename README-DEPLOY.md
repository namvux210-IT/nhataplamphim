# 🎬 PhimHub - Netflix-style Movie Streaming WebApp

Webapp xem phim hiện đại với thiết kế giống Netflix/Disney+, sử dụng OPhim API với Python proxy và caching.

![Deploy with Vercel](https://vercel.com/button)

## ✨ Tính năng

- 🎨 **Thiết kế hiện đại** - Giao diện giống Netflix/Disney+/Hulu
- 📱 **Responsive** - Hoạt động mượt mà trên mọi thiết bị
- 🚀 **Performance cao** - Caching thông minh, tốc độ load nhanh
- 🔍 **Tìm kiếm mạnh mẽ** - Tìm phim theo tên, thể loại, năm
- 🎞️ **Player nhúng** - Xem phim trực tiếp không quảng cáo
- 💾 **Double caching** - Cache server-side + client-side

## 🚀 Deploy lên Vercel (Khuyến nghị)

### Bước 1: Fork/Clone repo này về GitHub

```bash
git clone https://github.com/yourusername/phimhub.git
cd phimhub
```

### Bước 2: Deploy lên Vercel

#### Cách 1: Qua Vercel Dashboard (Dễ nhất)

1. Truy cập [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import repository GitHub của bạn
4. Vercel sẽ tự động phát hiện cấu hình và deploy
5. Đợi vài phút và done! 🎉

#### Cách 2: Qua Vercel CLI

```bash
# Cài đặt Vercel CLI
npm i -g vercel

# Deploy
vercel

# Hoặc deploy production
vercel --prod
```

### Bước 3: Tận hưởng!

Vercel sẽ cung cấp cho bạn URL dạng: `https://phimhub.vercel.app`

## 🏠 Chạy Local

### Option 1: Dùng Python Proxy (Full-featured)

```bash
# Cài đặt dependencies
pip install -r requirements.txt

# Chạy proxy server
python ophim_proxy.py

# Mở index.html trong trình duyệt
# Hoặc dùng Python HTTP server
python -m http.server 8000
```

Truy cập: `http://localhost:8000`

### Option 2: Chỉ frontend (Đơn giản)

```bash
# Mở trực tiếp file HTML
open index.html

# Hoặc dùng Live Server extension trong VS Code
```

**Lưu ý:** Khi chạy local, app sẽ tự động kết nối với Python proxy ở `localhost:5000`

## 📁 Cấu trúc project

```
phimhub/
├── api/
│   └── index.py           # Vercel serverless function
├── index.html             # Frontend webapp
├── ophim_proxy.py         # Python Flask proxy (local development)
├── requirements.txt       # Python dependencies (local)
├── requirements-vercel.txt # Python dependencies (Vercel)
├── vercel.json            # Vercel configuration
├── .gitignore
└── README.md
```

## 🔧 Cấu hình

### Vercel Edge Caching

Trong `vercel.json`, đã cấu hình cache 30 phút:

```json
{
  "key": "Cache-Control",
  "value": "s-maxage=1800, stale-while-revalidate"
}
```

### Environment Variables (Optional)

Bạn có thể thêm env vars trong Vercel Dashboard:

```
OPHIM_BASE_URL=https://ophim17.cc
```

## 🎯 API Endpoints

Tất cả endpoints đều có prefix `/api`:

### Danh sách phim

```
GET /api/danh-sach/phim-moi-cap-nhat?page=1
GET /api/danh-sach/phim-le?page=1
GET /api/danh-sach/phim-bo?page=1
GET /api/danh-sach/hoat-hinh?page=1
GET /api/danh-sach/tv-shows?page=1
```

### Chi tiết phim

```
GET /api/phim/{slug}
```

### Tìm kiếm

```
GET /api/v1/api/tim-kiem?keyword={query}&limit=20
```

### Thể loại & Quốc gia

```
GET /api/the-loai
GET /api/quoc-gia
```

## 🛠️ Tech Stack

- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Backend:** Python (Flask cho local, Serverless cho Vercel)
- **API:** OPhim API (https://ophim17.cc)
- **Hosting:** Vercel (Serverless Functions + Edge Caching)
- **Caching:** Multi-layer (Edge + Client-side)

## 🎨 Customization

### Đổi màu chủ đạo

Trong `index.html`, tìm CSS variables:

```css
:root {
    --primary-color: #e50914;  /* Đỏ Netflix */
    --secondary-color: #141414; /* Đen tối */
}
```

### Thêm thể loại mới

Trong `index.html`, tìm hàm `loadCategories()`:

```javascript
const categories = [
    { name: 'Phim mới', slug: 'phim-moi-cap-nhat' },
    { name: 'Phim lẻ', slug: 'phim-le' },
    // Thêm category mới tại đây
];
```

## 📊 Performance

- ⚡ Vercel Edge Network - CDN toàn cầu
- 💾 Edge caching 30 phút cho API responses
- 🚀 Client-side caching bổ sung
- 📦 Serverless functions - scale tự động

## 🔒 Bảo mật & Rate Limiting

Vercel tự động:
- Rate limiting cho serverless functions
- DDoS protection
- SSL/HTTPS miễn phí

## 🐛 Troubleshooting

### 1. "Failed to fetch" error

- **Local:** Đảm bảo `python ophim_proxy.py` đang chạy
- **Vercel:** Kiểm tra serverless function logs trong dashboard

### 2. CORS errors

- Vercel: Headers đã được cấu hình trong `vercel.json`
- Local: Flask-CORS xử lý tự động

### 3. API timeout

- OPhim API có thể chậm đôi khi
- Vercel functions có timeout 10s
- Cache giúp giảm thiểu vấn đề này

### 4. Phim không load

- Kiểm tra console log
- OPhim API có thể thay đổi cấu trúc
- Báo lỗi qua Issues

## 📝 TODO

- [ ] Thêm authentication
- [ ] Favorite movies list
- [ ] Watch history
- [ ] Comment system
- [ ] Rating system
- [ ] Admin panel
- [ ] PWA support

## 🤝 Contributing

Pull requests are welcome! Với các thay đổi lớn, vui lòng mở issue trước.

## 📄 License

MIT License - Tự do sử dụng và chỉnh sửa

## 🙏 Credits

- **OPhim API** - Nguồn phim miễn phí
- **Vercel** - Hosting miễn phí
- **Netflix/Disney+** - Design inspiration

## 📧 Contact

Có vấn đề? Tạo issue trên GitHub!

---

**Made with ❤️ for Vietnamese movie lovers**

⭐ Star repo này nếu bạn thấy hữu ích!
