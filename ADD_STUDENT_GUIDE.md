# Talaba Qo'shish Scriptlari

## 1. Kamera orqali (Tavsiya etiladi)

Kameradan yuzni aniqlaydi va avtomatik yuklaydi:

```bash
cd backend
python3 add_student_camera.py
```

**Qadamlar:**
1. Talaba ma'lumotlarini kiriting (ID, ism, email, telefon, kurs, guruh)
2. Kameraga qarang
3. `SPACE` - rasmni saqlash
4. `q` - chiqish

**Misol:**
```bash
cd backend
python3 add_student_camera.py

# Keyin:
Talaba ID: T2024001
Ism Familiya: Ali Valiyev
Email (ixtiyoriy): ali@example.com
Telefon (ixtiyoriy): +998901234567
Kurs (ixtiyoriy): 2
Guruh (ixtiyoriy): 2-A

# Kameraga qarang va SPACE bosib rasmni saqlang
```

## 2. Fayl orqali (Oddiy)

Rasm faylini ko'rsatib talaba qo'shish:

```bash
cd backend
python3 add_student_simple.py <student_id> <full_name> <image_path> [email] [phone] [course] [group]
```

**Misol:**
```bash
cd backend
python3 add_student_simple.py T2024001 "Ali Valiyev" /path/to/image.jpg

# Yoki to'liq ma'lumotlar bilan:
python3 add_student_simple.py T2024001 "Ali Valiyev" image.jpg ali@example.com +998901234567 2 2-A
```

## 3. Frontend orqali

1. http://localhost:3000 oching
2. "Talabalar" tab'iga o'ting
3. "+ Talaba Qo'shish" tugmasini bosing
4. Talaba ma'lumotlarini kiriting
5. Talaba yaratilgandan keyin, yuz rasmini yuklang (📷 Kamera yoki 📁 Fayl)

## Muhim Eslatmalar

1. **Backend ishlashi kerak** - http://localhost:8000
2. **Kamera permission** - Agar kamera ishlamasa:
   ```bash
   sudo usermod -a -G video $USER
   newgrp video
   ```
3. **Yuz aniqlanishi kerak** - Rasmda yuz aniq ko'rinishi kerak
4. **1-5 ta rasm** - Har bir talaba uchun maksimal 5 ta rasm yuklash mumkin
5. **Embedding avtomatik yaratiladi** - Rasm yuklangandan keyin

## Tekshirish

```bash
# Talabalar ro'yxatini ko'rish
curl http://localhost:8000/api/students

# Yoki frontend orqali
# http://localhost:3000
```

## Muammolar

### Kamera ishlamayapti
```bash
# Permission tekshirish
groups $USER

# Video group'ga qo'shish
sudo usermod -a -G video $USER
newgrp video

# Kamerani test qilish
python3 test_camera.py 0
```

### Backend ishlamayapti
```bash
# Backend ni ishga tushirish
cd backend
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Yuz aniqlanmayapti
- Yaxshi yoritilgan joyda bo'ling
- Kameraga to'g'ri qarang
- Yuz aniq ko'rinishi kerak
- Boshqa rasm yuklab ko'ring

