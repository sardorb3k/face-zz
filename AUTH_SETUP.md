# Authentication System Setup

## Yaratilgan Funksiyalar

### Backend
1. **Authentication System (JWT)**
   - Login endpoint (`/api/auth/login-json`)
   - User registration (admin only)
   - Role-based access control (student/admin)
   - Token verification

2. **Face Verification System**
   - Student face upload (`/api/verification/verify`)
   - Pending verifications list (admin)
   - Approve/Reject verification (admin)

3. **System Configuration**
   - RTSP camera configuration (admin)
   - General system configs (admin)

### Frontend
1. **Login Page** (`/login`)
   - Username/password login
   - Automatic redirect based on role

2. **Student Dashboard** (`/student`)
   - Face upload for verification
   - Verification status

3. **Admin Panel** (`/admin`)
   - Pending face verifications review
   - Approve/Reject verifications
   - RTSP camera configuration

4. **Main Dashboard** (`/`)
   - Role-based access
   - Links to student/admin panels

## Setup Instructions

### 1. Database Migration

Database avtomatik yangilanadi, lekin agar kerak bo'lsa:

```bash
cd backend
python3 -c "from app.database import init_db; init_db()"
```

### 2. Create Admin User

```bash
cd backend
python3 create_admin.py admin admin123 admin@example.com
```

Yoki Python orqali:
```python
from app.database import SessionLocal, init_db
from app.models import User

init_db()
db = SessionLocal()

admin = User(
    username="admin",
    email="admin@example.com",
    role="admin",
    is_active=True
)
admin.set_password("admin123")
db.add(admin)
db.commit()
```

### 3. Create Student User

Student user yaratish uchun avval talaba yaratish kerak:

```python
from app.database import SessionLocal
from app.models import Student, User

db = SessionLocal()

# Talaba yaratish
student = Student(
    student_id="ST001",
    full_name="John Doe",
    email="john@example.com"
)
db.add(student)
db.commit()
db.refresh(student)

# Student user yaratish
user = User(
    username="john_doe",
    email="john@example.com",
    role="student",
    student_id=student.id,
    is_active=True
)
user.set_password("student123")
db.add(user)
db.commit()
```

Yoki API orqali (admin login qilgan holda):
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "student123",
    "email": "john@example.com",
    "role": "student",
    "student_id": 1
  }'
```

## API Endpoints

### Authentication
- `POST /api/auth/login-json` - Login (JSON)
- `GET /api/auth/me` - Get current user
- `POST /api/auth/register` - Register user (admin only)

### Face Verification
- `POST /api/verification/verify` - Upload face for verification (student)
- `GET /api/verification/pending` - Get pending verifications (admin)
- `POST /api/verification/{id}/approve` - Approve verification (admin)
- `POST /api/verification/{id}/reject` - Reject verification (admin)

### Configuration
- `GET /api/config/rtsp/cameras` - Get RTSP cameras (admin)
- `POST /api/config/rtsp/cameras` - Set RTSP cameras (admin)

## Frontend Routes

- `/login` - Login page
- `/` - Main dashboard (requires login)
- `/student` - Student dashboard (student only)
- `/admin` - Admin panel (admin only)

## Environment Variables

Backend `.env` ga qo'shish:
```env
JWT_SECRET_KEY=your-secret-key-change-in-production
```

## Usage

1. **Admin Login:**
   - URL: http://localhost:3000/login
   - Username: admin
   - Password: admin123 (yoki yaratilgan parol)

2. **Student Login:**
   - URL: http://localhost:3000/login
   - Username: student_username
   - Password: student_password

3. **Student Face Upload:**
   - Login qilish
   - `/student` ga o'tish
   - Face rasmini yuklash
   - Verification request yuboriladi

4. **Admin Verification Review:**
   - Admin login qilish
   - `/admin` ga o'tish
   - Pending verifications ni ko'rish
   - Approve yoki Reject qilish

5. **RTSP Camera Configuration:**
   - Admin login qilish
   - `/admin` ga o'tish
   - "RTSP Cameras" tab
   - Camera qo'shish/sozlash

## Security Notes

- JWT token 7 kun amal qiladi
- Parollar SHA256 + salt bilan hash qilinadi
- Admin endpoints faqat admin role bilan ishlaydi
- Student endpoints faqat student role bilan ishlaydi

