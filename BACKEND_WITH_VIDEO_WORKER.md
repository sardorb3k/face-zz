# Backend ichida Video Worker

## ✅ Video Worker Endi Backend Ichida!

Video worker endi backend ichida background thread sifatida ishlaydi. Alohida process kerak emas!

## Xususiyatlar

1. **Avtomatik ishga tushish** - Backend ishga tushganda video worker ham ishga tushadi
2. **Bitta process** - Backend va video worker bir process'da
3. **Kamera muammosi yo'q** - Bitta process kamerani ishlatadi
4. **API orqali boshqarish** - Start/stop/status endpoint'lar

## Ishga Tushirish

### Oddiy usul (Tavsiya)

```bash
cd backend
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Video worker avtomatik ishga tushadi!

### Qayta ishga tushirish

```bash
cd backend
./restart_backend.sh
```

## API Endpoint'lar

### Video Worker Status
```bash
curl http://localhost:8000/api/video-worker/status
```

Response:
```json
{
  "running": true,
  "auto_start": true
}
```

### Video Worker Start
```bash
curl -X POST http://localhost:8000/api/video-worker/start
```

### Video Worker Stop
```bash
curl -X POST http://localhost:8000/api/video-worker/stop
```

## Konfiguratsiya

`.env` faylida:

```bash
# Video worker avtomatik ishga tushishi
AUTO_START_VIDEO_WORKER=true  # default: true

# Kamera sozlash
USE_LAPTOP_CAMERA=true
LAPTOP_CAMERA_INDEX=0
RTSP_CAMERAS=rtsp://...
```

## Afzalliklar

1. ✅ **Bitta process** - Backend va video worker bir process'da
2. ✅ **Kamera muammosi yo'q** - Bitta process kamerani ishlatadi
3. ✅ **Oson boshqarish** - API orqali start/stop
4. ✅ **Avtomatik** - Backend ishga tushganda avtomatik ishga tushadi
5. ✅ **Oson deploy** - Bitta process boshqarish osonroq

## Eslatmalar

- Video worker background thread sifatida ishlaydi
- Backend to'xtaganda video worker ham to'xtaydi
- Agar kamera sozlanganmagan bo'lsa, video worker ishga tushmaydi
- `AUTO_START_VIDEO_WORKER=false` qilib qo'lda boshqarish mumkin

## Eski Usul (Endi Kerak Emas)

❌ **Eski usul** (alohida process):
```bash
# Endi kerak emas!
python3 -m video_worker.main
```

✅ **Yangi usul** (backend ichida):
```bash
# Faqat backend ni ishga tushirish kifoya
python3 -m uvicorn app.main:app --reload
```

## Tekshirish

```bash
# Backend health
curl http://localhost:8000/health

# Video worker status
curl http://localhost:8000/api/video-worker/status

# Yoki browser'da
# http://localhost:8000/api/video-worker/status
```

