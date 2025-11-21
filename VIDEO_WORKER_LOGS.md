# Video Worker Loglari

## Console Loglari

Video worker ishga tushganda quyidagi loglar chiqadi:

### 1. Talaba Aniqlanganda

```
🎓 Talaba aniqlandi: Student ID 1 (confidence: 0.856, track: 5, camera: 1)
Attendance logged: Student 1 on camera 1 (confidence: 0.856)
```

### 2. Yuz Aniqlandi, Lekin Talaba Tanilmadi

```
📸 1 ta yuz aniqlandi (camera: 1)
❓ Yuz aniqlandi, lekin talaba tanilmadi (track: 5, camera: 1)
```

### 3. Duplicate Prevention

```
🎓 Talaba aniqlandi: Student ID 1 (confidence: 0.856, track: 5, camera: 1)
⚠️  Duplicate prevention: Student 1 on camera 1 - attendance not logged
```

### 4. Yuzlar Aniqlanganda

```
📸 2 ta yuz aniqlandi (camera: 1)
🎓 Talaba aniqlandi: Student ID 1 (confidence: 0.856, track: 5, camera: 1)
🎓 Talaba aniqlandi: Student ID 2 (confidence: 0.742, track: 6, camera: 1)
```

## Log Darajalari

- **INFO**: Talaba aniqlanganda, attendance yozilganda
- **DEBUG**: Yuzlar aniqlandi, lekin tanilmadi, duplicate prevention

## Log Format

```
YYYY-MM-DD HH:MM:SS,mmm - module_name - LEVEL - Message
```

Misol:
```
2025-11-21 16:41:33,373 - __main__ - INFO - 🎓 Talaba aniqlandi: Student ID 1 (confidence: 0.856, track: 5, camera: 1)
2025-11-21 16:41:33,374 - video_worker.attendance_manager - INFO - Attendance logged: Student 1 on camera 1 (confidence: 0.856)
```

## Debug Mode

Barcha loglarni ko'rish uchun log level'ni DEBUG ga o'zgartiring:

```python
# backend/video_worker/main.py yoki config'da
logging.basicConfig(level=logging.DEBUG)
```

## Muhim Loglar

1. **Talaba aniqlanganda**: `🎓 Talaba aniqlandi: Student ID X`
2. **Attendance yozilganda**: `Attendance logged: Student X on camera Y`
3. **Duplicate prevention**: `⚠️  Duplicate prevention`
4. **Yuz topilmadi**: `❓ Yuz aniqlandi, lekin talaba tanilmadi`

