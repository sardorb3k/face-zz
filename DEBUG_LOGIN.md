# Login Debug Guide

## Tekshirish

### 1. Browser Console'ni oching (F12)
Login qilishda quyidagi loglar ko'rinishi kerak:

```
Login attempt: {username: "student", password: "***"}
Sending login request to: http://localhost:8000/api/auth/login-json
Request body: {username: "student", password: "***"}
Response status: 200
Response ok: true
Login response data: {...}
Setting auth state...
Login successful, user: {...}
Login result: {success: true, user: {...}}
Redirecting user: {...}
Redirecting to /student
```

### 2. Agar Error bo'lsa

**Network Error:**
- Backend ishlayaptimi: `curl http://localhost:8000/health`
- CORS muammosi bo'lishi mumkin

**401 Unauthorized:**
- Username yoki password noto'g'ri
- User active emas

**Invalid response:**
- Backend response format noto'g'ri

### 3. Manual Test

Browser console'da:
```javascript
// Test login
fetch('http://localhost:8000/api/auth/login-json', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({username: 'student', password: 'student123'})
})
.then(r => r.json())
.then(data => {
  console.log('Success:', data);
  localStorage.setItem('auth_token', data.access_token);
  localStorage.setItem('auth_user', JSON.stringify(data.user));
  window.location.href = '/student';
})
.catch(err => console.error('Error:', err));
```

### 4. Database Tekshirish

```bash
cd backend
python3 -c "from app.database import SessionLocal; from app.models import User; db = SessionLocal(); u = db.query(User).filter(User.username == 'student').first(); print(f'User: {u.username}, Active: {u.is_active}, Password check: {u.check_password(\"student123\")}')"
```

### 5. Common Issues

**Issue: "Login failed"**
- Browser console'da error'ni ko'ring
- Network tab'da request'ni tekshiring

**Issue: Redirect ishlamayapti**
- Router.push() ishlayaptimi tekshiring
- Browser console'da redirect log'ini ko'ring

**Issue: Token saqlanmayapti**
- localStorage'ni tekshiring: `localStorage.getItem('auth_token')`
- Browser'da localStorage blocked bo'lishi mumkin

