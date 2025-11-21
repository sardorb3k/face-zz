# Oddiy Kameradan Ishga Tushirish

## 1. Kamerani Tekshirish

```bash
# Kamerani topish
ls -la /dev/video*

# Yoki
v4l2-ctl --list-devices
```

Agar kamera topilmasa:
```bash
# User'ni video group'ga qo'shish
sudo usermod -a -G video $USER

# Keyin logout/login qiling yoki:
newgrp video
```

## 2. Backend ni Ishga Tushirish

Terminal 1:
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Yoki:
```bash
cd backend
python run.py
```

## 3. Video Worker ni Ishga Tushirish

Terminal 2:
```bash
cd backend
python -m video_worker.main
```

Yoki:
```bash
cd backend
python run_worker.py
```

## 4. Frontend ni Ishga Tushirish

Terminal 3:
```bash
cd frontend
npm run dev
```

## Yoki Barchasini Bir Vaqtda

```bash
./start.sh
```

## Tekshirish

1. Backend: http://localhost:8000
2. Frontend: http://localhost:3000
3. Health check: http://localhost:8000/health

## Muammolar

### Kamera topilmayapti
```bash
# Permission tekshirish
groups $USER

# Video group'ga qo'shish
sudo usermod -a -G video $USER
newgrp video
```

### Kamera index o'zgartirish
`.env` faylida:
```
LAPTOP_CAMERA_INDEX=0  # 0, 1, 2, ...
```

### Video worker xatolik
- Kamerani boshqa dastur ishlatmayotganini tekshiring
- `LAPTOP_CAMERA_INDEX` ni o'zgartiring
- Log'larni tekshiring

