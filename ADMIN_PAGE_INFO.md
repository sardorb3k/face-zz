# Admin Page Ma'lumotlari

## Admin Page Funksiyalari

### 1. Face Verifications Tab
- **Pending Face Verifications** - Talabalar tomonidan yuborilgan yuz tasdiqlash so'rovlari
- **Approve** - Yuzni tasdiqlash (student image'ga qo'shiladi)
- **Reject** - Yuzni rad etish (rasm o'chiriladi)
- Har bir verification'da ko'rsatiladi:
  - Student name
  - Student ID
  - Confidence (aniqlik)
  - Created date
  - Face image preview

### 2. RTSP Cameras Tab
- **Add New Camera** - Yangi RTSP kamera qo'shish
  - Camera Name
  - RTSP URL (rtsp://...)
- **Camera List** - Sozlangan kameralar ro'yxati

## Admin Login

**URL:** http://localhost:3000/login

**Credentials:**
- Username: `admin`
- Password: `admin123`

**Admin Page URL:** http://localhost:3000/admin

## Muammo Hal Qilish

### Agar Admin Page'ga kira olmasangiz:

1. **Browser Console'ni oching (F12)**
   - Console'da error'lar bor-yo'qligini tekshiring
   - Network tab'da request'larni ko'ring

2. **Login tekshirish:**
   ```bash
   curl -X POST http://localhost:8000/api/auth/login-json \
     -H "Content-Type: application/json" \
     -d '{"username":"admin","password":"admin123"}'
   ```

3. **Database tekshirish:**
   ```bash
   cd backend
   python3 -c "from app.database import SessionLocal; from app.models import User; db = SessionLocal(); u = db.query(User).filter(User.username == 'admin').first(); print(f'Admin: {u.username}, Role: {u.role}, Active: {u.is_active}')"
   ```

4. **Auth state tekshirish:**
   Browser console'da:
   ```javascript
   console.log('Token:', localStorage.getItem('auth_token'));
   console.log('User:', JSON.parse(localStorage.getItem('auth_user') || '{}'));
   ```

## Admin Page Features

### Face Verifications
- Talabalar tomonidan yuborilgan yuz tasdiqlash so'rovlarini ko'rish
- Har bir so'rovni approve yoki reject qilish
- Student image'ga qo'shish (approve qilinganda)

### RTSP Cameras
- RTSP kameralarni sozlash
- Camera qo'shish/o'chirish
- Camera URL'larini boshqarish

## Keyingi Qadamlar

1. Admin login qiling
2. `/admin` ga o'ting
3. Face Verifications tab'da pending verification'larni ko'ring
4. RTSP Cameras tab'da kameralarni sozlang

