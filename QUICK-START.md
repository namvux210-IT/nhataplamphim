# 🚀 Hướng dẫn Deploy nhanh lên Vercel

## Bước 1: Tạo GitHub Repository

```bash
# Khởi tạo git
git init

# Add tất cả files
git add .

# Commit
git commit -m "Initial commit - PhimHub webapp"

# Tạo repo mới trên GitHub rồi push
git remote add origin https://github.com/YOUR_USERNAME/phimhub.git
git branch -M main
git push -u origin main
```

## Bước 2: Deploy lên Vercel

### Cách 1: Qua Dashboard (Khuyến nghị - Dễ nhất)

1. Truy cập https://vercel.com
2. Đăng nhập bằng GitHub
3. Click **"Add New..."** → **"Project"**
4. Chọn repository `phimhub` từ danh sách
5. Click **"Import"**
6. Vercel sẽ tự động detect settings:
   - Framework Preset: Other
   - Build Command: (để trống)
   - Output Directory: (để trống)
7. Click **"Deploy"**
8. Đợi 1-2 phút ⏰
9. **Done!** 🎉 Copy link và chia sẻ

### Cách 2: Qua Vercel CLI

```bash
# Cài Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel

# Hoặc deploy thẳng production
vercel --prod
```

## Bước 3: Kiểm tra

Truy cập URL Vercel cung cấp, ví dụ:
```
https://phimhub-abc123.vercel.app
```

Nếu mọi thứ OK, bạn sẽ thấy:
✅ Trang chủ với hero banner
✅ Danh sách phim load thành công
✅ Tìm kiếm hoạt động
✅ Xem phim được

## 🔍 Troubleshooting

### "Deployment failed" 

Kiểm tra:
- Tất cả files đã được push lên GitHub chưa
- `vercel.json` có đúng format không
- `requirements.txt` có file không

### Phim không load

Mở Console (F12) để xem lỗi:
- Nếu "404": Kiểm tra API routes trong `vercel.json`
- Nếu "CORS": Headers đã được config trong `vercel.json`
- Nếu "Timeout": OPhim API có thể đang chậm

### Custom Domain

Trong Vercel Dashboard:
1. Vào project settings
2. Tab "Domains"
3. Add your domain
4. Follow DNS instructions

## 📊 Monitor

Vercel Dashboard cho bạn:
- Analytics
- Function logs
- Error tracking
- Performance metrics

## 🎯 Next Steps

Sau khi deploy thành công:

1. ⭐ Star repo trên GitHub
2. 📝 Cập nhật README với URL live
3. 🎨 Customize theme theo ý bạn
4. 🚀 Share với bạn bè!

## 💡 Pro Tips

- Enable Vercel Analytics để track visitors
- Set up custom domain cho professional
- Use Environment Variables cho config
- Enable Edge Caching để tăng tốc

---

**Có vấn đề?** Tạo Issue trên GitHub hoặc check Vercel docs!

Happy coding! 🎬
