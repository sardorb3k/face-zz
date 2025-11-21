# Servislarni Ishga Tushirish

## ✅ Backend - Allaqachon ishlayapti!

Backend http://localhost:8000 da ishlayapti.

## Video Worker ni Ishga Tushirish

**Yangi Terminal oching va quyidagilarni bajaring:**

```bash
cd ~/apps/face-r/backend
python3 -m video_worker.main
```

Yoki:
```bash
cd ~/apps/face-r/backend
python3 run_worker.py
```

Video worker:
- Kamerani ulaydi
- Yuzlarni aniqlaydi
- Talabalarni tanib oladi
- Davomatni yozadi

## Frontend ni Ishga Tushirish

**Yana bir yangi Terminal oching:**

```bash
cd ~/apps/face-r/frontend
npm run dev
```

Frontend http://localhost:3000 da ochiladi.

## Tekshirish

1. Backend: http://localhost:8000
2. Frontend: http://localhost:3000
3. Admin panel: http://localhost:3000

## Muammolar

### Video worker kamerani topa olmayapti
```bash
# Permission tekshirish
groups $USER

# Video group'ga qo'shish
sudo usermod -a -G video $USER
newgrp video
```

### Port band
```bash
# Qaysi process portni ishlatayotganini topish
lsof -ti:8000

# Process ni to'xtatish (agar kerak bo'lsa)
kill <PID>
```

