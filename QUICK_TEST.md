# Student Login Tekshirish

## Backend Test (✅ Ishlayapti)

```bash
curl -X POST http://localhost:8000/api/auth/login-json \
  -H "Content-Type: application/json" \
  -d '{"username":"student","password":"student123"}'
```

Response:
```json
{
  "access_token": "...",
  "token_type": "bearer",
  "user": {
    "id": 2,
    "username": "student",
    "email": "student@face-r.local",
    "role": "student",
    "student_id": 3
  }
}
```

## Frontend Test

1. **Frontend ni ishga tushiring:**
```bash
cd frontend
npm run dev
```

2. **Browser'da oching:**
   - http://localhost:3000/login

3. **Login qiling:**
   - Username: `student`
   - Password: `student123`

4. **Browser Console'ni oching (F12):**
   - Network tab'da login request'ni ko'ring
   - Console'da error bormi tekshiring

## Muammo Bo'lsa

### 1. CORS Muammosi
Backend'da CORS sozlanmagan bo'lishi mumkin. Tekshiring:
```bash
cd backend
grep -r "CORSMiddleware" app/main.py
```

### 2. API URL Muammosi
Frontend `.env.local` faylida:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Browser Cache
Browser cache'ni tozalang:
- Ctrl+Shift+R (hard refresh)
- Yoki Incognito mode'da oching

### 4. Network Error
Browser console'da network error ko'rsangiz:
- Backend ishlayaptimi tekshiring: `curl http://localhost:8000/health`
- Frontend API URL to'g'rimi tekshiring

## Debug

Browser console'da:
```javascript
// Test login
fetch('http://localhost:8000/api/auth/login-json', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({username: 'student', password: 'student123'})
})
.then(r => r.json())
.then(console.log)
.catch(console.error)
```

