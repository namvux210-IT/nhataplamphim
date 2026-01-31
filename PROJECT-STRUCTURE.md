# 📁 Cấu trúc Project - PhimHub

```
phimhub/
│
├── 📁 api/                          # Vercel Serverless Functions
│   └── index.py                     # Python API proxy cho Vercel
│
├── 📄 index.html                    # Frontend webapp chính
│                                    # - Responsive design
│                                    # - Netflix-style UI
│                                    # - Auto-detect local/production
│
├── 🐍 ophim_proxy.py                # Flask proxy cho local development
│                                    # - Chỉ dùng khi dev local
│                                    # - Full caching với Flask-Caching
│
├── ⚙️ vercel.json                   # Vercel deployment config
│                                    # - Routes configuration
│                                    # - CORS headers
│                                    # - Edge caching
│
├── 📦 requirements.txt              # Python deps cho Vercel
│   └── requests==2.31.0             # (chỉ cần requests cho serverless)
│
├── 📦 requirements-local.txt        # Python deps cho local dev
│   ├── Flask==3.0.0                 # Web framework
│   ├── flask-cors==4.0.0            # CORS support
│   ├── flask-caching==2.1.0         # Caching
│   └── requests==2.31.0             # HTTP client
│
├── 📦 package.json                  # Node.js metadata
│                                    # - Scripts cho dev
│                                    # - Project info
│
├── 🚫 .gitignore                    # Git ignore rules
│   ├── __pycache__/                 # Python cache
│   ├── .vercel/                     # Vercel local config
│   └── *.log                        # Log files
│
├── 📖 README-DEPLOY.md              # Hướng dẫn chi tiết
│                                    # - Features
│                                    # - Deployment
│                                    # - Customization
│
└── 📖 QUICK-START.md                # Hướng dẫn nhanh deploy
                                     # - 3 bước đơn giản
                                     # - Troubleshooting

```

## 🔄 Workflow

### Local Development:
```
1. Chạy Flask proxy: python ophim_proxy.py
2. Mở index.html trong browser
3. App tự động connect tới localhost:5000
```

### Production (Vercel):
```
1. Push code lên GitHub
2. Vercel auto-build và deploy
3. Serverless functions handle API
4. Edge caching optimize performance
```

## 🌐 URL Structure

### Local:
- Frontend: `http://localhost:8000`
- API Proxy: `http://localhost:5000/api/*`

### Production (Vercel):
- Frontend: `https://your-app.vercel.app`
- API: `https://your-app.vercel.app/api/*`

## 💾 Caching Strategy

```
┌─────────────┐
│   Browser   │ ← Client cache (30 min)
└──────┬──────┘
       │
┌──────▼──────┐
│ Vercel Edge │ ← Edge cache (30 min)
└──────┬──────┘
       │
┌──────▼──────┐
│  OPhim API  │ ← Source data
└─────────────┘
```

## 🎯 Files Bạn Cần Upload GitHub

**Required cho Vercel:**
✅ api/index.py
✅ index.html
✅ vercel.json
✅ requirements.txt

**Optional nhưng nên có:**
✅ .gitignore
✅ README-DEPLOY.md
✅ QUICK-START.md
✅ package.json

**Không cần (chỉ dùng local):**
❌ ophim_proxy.py (optional nếu muốn chạy local)
❌ requirements-local.txt
❌ movie-webapp.html (là bản cũ)

## 🔧 Customize

Muốn thay đổi gì?

**🎨 Theme/Colors:**
→ Edit CSS trong `index.html`

**🔌 API Endpoints:**
→ Edit `api/index.py`

**⚙️ Cache Duration:**
→ Edit `vercel.json` (Edge cache)
→ Edit `index.html` (Client cache)

**🌐 Domain:**
→ Add trong Vercel Dashboard

## 📝 Development Checklist

Trước khi deploy:

- [ ] Test local với Python proxy
- [ ] Check responsive design (mobile/tablet)
- [ ] Test search functionality
- [ ] Test video player
- [ ] Update README với project info
- [ ] Add .gitignore
- [ ] Commit và push lên GitHub
- [ ] Deploy lên Vercel
- [ ] Test production URL
- [ ] Share với bạn bè! 🎉

---

**Need help?** Check QUICK-START.md hoặc README-DEPLOY.md
