# Kamera Muammosini Hal Qilish

## Muammo

Kamera video worker tomonidan ishlatilmoqda, shuning uchun script kameraga ulanib bo'layapti.

## Yechimlar

### 1. Video Worker ni Vaqtinchalik To'xtatish (Tavsiya)

```bash
# Video worker process'ni topish
ps aux | grep video_worker

# To'xtatish
kill <PID>

# Yoki Ctrl+C orqali to'xtatish (terminal'da)
```

Keyin scriptni ishga tushiring:
```bash
python3 add_student_camera.py
```

### 2. Fayl Orqali Talaba Qo'shish

Kameradan foydalanmasdan, rasm faylini ishlatish:

```bash
python3 add_student_simple.py T2024001 "Ali Valiyev" /path/to/image.jpg
```

### 3. Frontend Orqali

1. http://localhost:3000 oching
2. Talabalar tab'iga o'ting
3. "+ Talaba Qo'shish" tugmasini bosing
4. Talaba yaratilgandan keyin, yuz rasmini yuklang

### 4. Video Worker ni Qayta Ishga Tushirish

Talaba qo'shgandan keyin:

```bash
cd backend
python3 -m video_worker.main
```

## Tekshirish

```bash
# Qaysi process kamerani ishlatayotganini topish
lsof /dev/video0

# Video worker ni to'xtatish
pkill -f video_worker
```

