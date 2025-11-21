# Tizim Holati

## ✅ Ishlamoqda

1. **Backend**: http://localhost:8000 ✅
2. **Frontend**: http://localhost:3000 ✅
3. **Video Worker**: PID 85321 ✅

## ⚠️ Muammolar

### 1. Kamera Video Worker tomonidan ishlatilmoqda

**Muammo**: Video worker (PID: 85321) kamerani ishlatmoqda, shuning uchun boshqa scriptlar kameraga ulana olmayapti.

**Yechim**:
```bash
# Video worker ni to'xtatish (agar kerak bo'lsa)
pkill -f video_worker

# Yoki talaba qo'shish uchun fayl orqali
cd backend
python3 add_student_file.py T2024001 "Ali Valiyev" /path/to/image.jpg
```

### 2. User Video Group'da Emas

**Muammo**: User video group'da emas, lekin video worker ishlayapti.

**Yechim**:
```bash
# User'ni video group'ga qo'shish
sudo usermod -a -G video $USER

# Keyin logout/login yoki:
newgrp video
```

## Tekshirish

```bash
# Tizim holatini tekshirish
cd backend
python3 check_system.py
```

## Video Worker Loglari

Video worker ishga tushganda console'da quyidagi loglar chiqadi:

- `🎓 Talaba aniqlandi: Student ID X` - Talaba aniqlanganda
- `Attendance logged: Student X on camera Y` - Attendance yozilganda
- `⚠️  Duplicate prevention` - Duplicate oldini olish

## Barcha Servislar

1. **Backend**: `python3 -m uvicorn app.main:app --reload`
2. **Video Worker**: `python3 -m video_worker.main`
3. **Frontend**: `npm run dev` (frontend papkasida)

