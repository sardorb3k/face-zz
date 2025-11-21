# Real-Time Face Detection - O'rnatish

## 📦 O'rnatish

### 1. Package'larni yuklash

```bash
cd frontend
npm install
```

Bu quyidagi yangi package'larni yuklaydi:
- `@mediapipe/face_detection` - Face detection model
- `@mediapipe/camera_utils` - Camera utilities  
- `@mediapipe/drawing_utils` - Drawing utilities

### 2. Frontend'ni ishga tushirish

```bash
npm run dev
```

## ✅ Test Qilish

1. Browser'da `http://localhost:3000` ga kirish
2. "Talabalar" tab'iga o'tish
3. Biror talaba qatorida **📷 Kamera** tugmasini bosish
4. Kameraga ruxsat bering
5. **Yuzingizni kameraga qarab turing**

### Kutilayotgan Natija

**Yuz aniqlanmadi-yu:**
- ⚠️ Sariq guide overlay ko'rinadi
- "⏳ Yuzni Kutmoqda..." tugmasi ko'rsatiladi
- Tugma o'chirilgan (disabled)

**Yuz aniqlandi-yu:**
- ✅ Yashil bounding box ko'rinadi
- "✅ Yuz aniqlandi! 95%" xabari ko'rsatiladi
- "📸 Rasm Olish" tugmasi faollashadi

## 🔧 Texnik Tafsilotlar

### MediaPipe Face Detection

- **Model**: `short` (tez va samarali)
- **Min Confidence**: 0.5
- **Real-time**: 30+ FPS
- **CDN**: Avtomatik yuklanadi

### Browser Support

- ✅ Chrome/Edge (eng yaxshi)
- ✅ Firefox
- ✅ Safari (iOS 14+)
- ⚠️ Eski browser'lar (fallback)

## 🐛 Muammolar

### 1. MediaPipe Yuklanmayapti

**Xatolik**: `Failed to load MediaPipe model`

**Yechim**:
- Internet aloqasini tekshiring
- CDN'ga kirish imkoniyatini tekshiring
- Browser console'da xatolarni ko'ring

### 2. Kamera Ishlamayapti

**Xatolik**: `Kameraga kirish imkoni yo'q`

**Yechim**:
- Browser sozlamalarida kamera ruxsatini bering
- HTTPS ishlatish kerak (localhost'da ishlaydi)

### 3. Face Detection Sekin

**Yechim**:
- Video resolution'ni pasaytiring
- Model'ni `short` dan `full` ga o'zgartiring (ancha sekin)

## 📝 Kod O'zgarishlari

### Yangi State'lar

```typescript
const [faceDetected, setFaceDetected] = useState(false)
const [faceDetectionResult, setFaceDetectionResult] = useState<FaceDetectionResult | null>(null)
```

### Yangi Refs

```typescript
const overlayCanvasRef = useRef<HTMLCanvasElement>(null)
const faceDetectionRef = useRef<FaceDetection | null>(null)
const cameraRef = useRef<Camera | null>(null)
```

### Real-Time Detection

```typescript
faceDetection.onResults((results) => {
  // Bounding box chizish
  // State yangilash
  // UI update
})
```

## ✅ Xulosa

Real-time face detection qo'shildi va ishga tayyor!

---

**🎉 Endi kamera orqali yuz yuklashda real-time detection ishlaydi!**

