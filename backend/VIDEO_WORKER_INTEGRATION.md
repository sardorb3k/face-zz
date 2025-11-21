# Video Worker Backend Integratsiyasi

## ✅ Video Worker Endi Backend Ichida!

Video worker endi backend ichida background thread sifatida ishlaydi.

## Xususiyatlar

1. **Avtomatik ishga tushish** - Backend ishga tushganda video worker ham ishga tushadi
2. **Background thread** - Alohida process emas, thread sifatida
3. **API orqali boshqarish** - Start/stop/status endpoint'lar
4. **Avtomatik to'xtash** - Backend to'xtaganda video worker ham to'xtaydi

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

## API Endpoint'lar

### Video Worker Status
```bash
GET /api/video-worker/status
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
POST /api/video-worker/start
```

### Video Worker Stop
```bash
POST /api/video-worker/stop
```

## Ishga Tushirish

### 1. Backend ni ishga tushirish

```bash
cd backend
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Video worker avtomatik ishga tushadi (agar kamera sozlangan bo'lsa).

### 2. Video Worker ni Qo'lda Boshqarish

```bash
# Status tekshirish
curl http://localhost:8000/api/video-worker/status

# To'xtatish
curl -X POST http://localhost:8000/api/video-worker/stop

# Ishga tushirish
curl -X POST http://localhost:8000/api/video-worker/start
```

## Afzalliklar

1. **Bitta process** - Backend va video worker bir process'da
2. **Kamera muammosi yo'q** - Bitta process kamerani ishlatadi
3. **Oson boshqarish** - API orqali start/stop
4. **Avtomatik** - Backend ishga tushganda avtomatik ishga tushadi

## Eslatmalar

- Video worker background thread sifatida ishlaydi
- Backend to'xtaganda video worker ham to'xtaydi
- Agar kamera sozlanganmagan bo'lsa, video worker ishga tushmaydi
- `AUTO_START_VIDEO_WORKER=false` qilib qo'lda boshqarish mumkin

