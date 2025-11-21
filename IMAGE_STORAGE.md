# Yuz Rasmlari Saqlash Joyi

## Papka Strukturasi

```
backend/data/
├── student_images/          # Talabalarning yuklangan yuz rasmlari
│   ├── 1_uuid1.jpg
│   ├── 1_uuid2.jpg
│   ├── 2_uuid1.jpg
│   └── ...
├── detected_faces/          # Video worker tomonidan aniqlangan yuzlar
│   ├── 1_1_uuid1.jpg
│   ├── 1_2_uuid2.jpg
│   └── ...
└── attendance.db            # SQLite database
```

## Yuz Rasmlari Joylashuvi

### 1. Talabalar Yuz Rasmlari
**Papka:** `backend/data/student_images/`

- Har bir talaba uchun 1-5 ta rasm saqlanadi
- Format: `{student_id}_{uuid}.{extension}`
- Masalan: `1_a1b2c3d4.jpg`, `1_e5f6g7h8.png`

**API orqali ko'rish:**
```
http://localhost:8000/static/student_images/{filename}
```

### 2. Aniqlangan Yuzlar (Detected Faces)
**Papka:** `backend/data/detected_faces/`

- Video worker tomonidan aniqlangan yuzlar
- Format: `{student_id}_{camera_id}_{uuid}.jpg`
- Masalan: `1_1_a1b2c3d4.jpg`

**API orqali ko'rish:**
```
http://localhost:8000/static/detected_faces/{filename}
```

## Konfiguratsiya

`.env` faylida:
```bash
DATA_DIR=./data                    # Asosiy data papkasi
# Yoki absolute path:
DATA_DIR=/home/sardor/apps/face-r/backend/data
```

## Database'da Saqlanishi

- `student_images` jadvalida `image_path` maydoni to'liq yo'lni saqlaydi
- `attendance_logs` jadvalida `image_path` maydoni detected face yo'lni saqlaydi

## Frontend'da Ko'rsatish

```typescript
// Student image
const imageUrl = `${API_URL}/static/student_images/${imagePath}`

// Detected face
const detectedImageUrl = `${API_URL}/static/detected_faces/${imagePath}`
```

## Muhim Eslatmalar

1. **Papkalar avtomatik yaratiladi** - Backend ishga tushganda
2. **Rasmlar database'da ham saqlanadi** - `image_path` maydoni orqali
3. **Static file serving** - FastAPI orqali rasmlarni ko'rish mumkin
4. **Backup** - `backend/data/` papkasini backup qilish tavsiya etiladi

## Tekshirish

```bash
# Papkalarni ko'rish
ls -la backend/data/student_images/
ls -la backend/data/detected_faces/

# Rasmlar soni
find backend/data/student_images -type f | wc -l
find backend/data/detected_faces -type f | wc -l
```

