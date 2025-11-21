# MediaPipe Package O'rnatish - Xatolik Tuzatish

## ✅ Qilingan

Package'lar o'rnatildi:
- ✅ `@mediapipe/face_detection@0.4.1646425229`
- ✅ `@mediapipe/camera_utils@0.3.1675466862`
- ✅ `@mediapipe/drawing_utils@0.3.1675466124`

## 🔄 Keyingi Qadamlar

### 1. Next.js Dev Server'ni Qayta Ishga Tushirish

Agar dev server ishlayotgan bo'lsa, uni to'xtatib qayta ishga tushiring:

```bash
# Terminal'da Ctrl+C bosib to'xtating
# Keyin qayta ishga tushiring:
cd frontend
npm run dev
```

### 2. Browser Cache'ni Tozalash

Agar hali ham xatolik bo'lsa:

1. Browser'da **Hard Refresh** qiling:
   - **Chrome/Edge**: `Ctrl+Shift+R` (Linux) yoki `Cmd+Shift+R` (Mac)
   - **Firefox**: `Ctrl+F5` (Linux) yoki `Cmd+Shift+R` (Mac)

2. Yoki Browser DevTools → Network → "Disable cache" ni yoqing

### 3. Next.js Cache'ni Tozalash

```bash
cd frontend
rm -rf .next
npm run dev
```

## 🐛 Muammolar

### Xatolik: "Module not found"

**Yechim 1**: Package'lar to'g'ri o'rnatilganini tekshiring:
```bash
cd frontend
npm list @mediapipe/face_detection
```

**Yechim 2**: `node_modules` ni qayta o'rnatish:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Xatolik: "TypeScript error"

**Yechim**: TypeScript cache'ni tozalash:
```bash
cd frontend
rm -rf .next
npm run dev
```

## ✅ Test Qilish

1. Dev server ishga tushganini tekshiring
2. Browser'da `http://localhost:3000` ga kirish
3. "Talabalar" → "Kamera" tugmasini bosish
4. Kameraga ruxsat bering
5. Yuzingizni kameraga qarab turing

**Kutilayotgan natija**: Yashil bounding box ko'rinishi kerak!

---

**🎉 Package'lar o'rnatildi, endi Next.js'ni qayta ishga tushiring!**

