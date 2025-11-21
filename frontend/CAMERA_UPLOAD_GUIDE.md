# Kamera orqali Yuz Yuklash - Qo'llanma

## 🎯 Funksiya

Frontend'ga kamera orqali yuz yuklash funksiyasi qo'shildi. Bu 2 bosqichli jarayon:

### 1-bosqich: Yuzni Olish 📸
- Real-time camera preview
- Face guide overlay (yuz qayerda bo'lishi kerakligini ko'rsatadi)
- To'liq yuzni olish (bosh va bo'yin bilan)
- Yaxshi yoritilgan joyda bo'lish tavsiyasi

### 2-bosqich: Test Qilish 🔍
- Yuz embedding yaratish
- Test qilish (ishlayaptimi yo'qmi)
- Confidence ko'rsatish
- "Bo'ldi" tugmasi (muvaffaqiyatli bo'lsa)

## 🚀 Ishlatish

### Talabalar ro'yxatida

1. Talabalar ro'yxatiga o'ting
2. Talaba qatorida **📷 Kamera** tugmasini bosing
3. Kameraga ruxsat bering
4. To'liq yuzingiz ko'rinishini ta'minlang
5. **📸 Rasm Olish** tugmasini bosing
6. **🔍 Test Qilish** tugmasini bosing
7. Agar muvaffaqiyatli bo'lsa, **✅ Bo'ldi** tugmasini bosing

## 📋 Qadamlari

### Step 1: Camera Preview
```
┌─────────────────────────┐
│  📸 1-bosqich: Yuzni Olish │
│                          │
│  [Camera Preview]       │
│  [Face Guide Overlay]    │
│                          │
│  [Bekor] [📸 Rasm Olish] │
└─────────────────────────┘
```

### Step 2: Testing
```
┌─────────────────────────┐
│  🔍 2-bosqich: Test Qilish │
│                          │
│  [Captured Image]       │
│                          │
│  ✅ Yuz aniqlandi!       │
│  Ishonchlilik: 95%      │
│                          │
│  [🔄 Qayta] [✅ Bo'ldi]  │
└─────────────────────────┘
```

### Step 3: Success
```
┌─────────────────────────┐
│         🎉               │
│    Muvaffaqiyatli!      │
│                          │
│  Yuz yuklandi va        │
│  embedding yaratildi    │
│                          │
│      [Yopish]           │
└─────────────────────────┘
```

## 🔧 Backend API

### Test Endpoint

```http
POST /api/upload/face/test?student_id={id}
Content-Type: multipart/form-data

Response:
{
  "success": true,
  "message": "Yuz muvaffaqiyatli aniqlandi",
  "confidence": 0.95,
  "embedding_created": true
}
```

### Upload Endpoint

```http
POST /api/upload/face?student_id={id}
Content-Type: multipart/form-data

Response:
{
  "success": true,
  "message": "Yuz rasmi muvaffaqiyatli yuklandi",
  "student_id": 5,
  "embedding_created": true
}
```

## 💡 Tavsiyalar

1. **Yoritish**: Yaxshi yoritilgan joyda bo'ling
2. **Pozitsiya**: To'g'ri qarab turing (yuz to'g'ri ko'rinishi kerak)
3. **Masofa**: Kameradan 50-100 cm masofada bo'ling
4. **To'liq yuz**: Bosh va bo'yin ko'rinishi kerak
5. **Qulaylik**: Qulay pozitsiyada bo'ling

## 🐛 Xatoliklar

### Kameraga kirish imkoni yo'q
- Browser ruxsatini tekshirish
- HTTPS ishlatish (production'da)
- Camera boshqa dasturda ishlatilmayotganini tekshirish

### Yuz aniqlanmadi
- Yaxshiroq yoritish
- To'g'ri qarab turish
- Masofani o'zgartirish

### Test muvaffaqiyatsiz
- Qayta rasm olish
- Yaxshiroq yoritish
- To'liq yuz ko'rinishini ta'minlash

## 📱 Browser Support

- ✅ Chrome/Edge (eng yaxshi)
- ✅ Firefox
- ✅ Safari (iOS 11+)
- ⚠️ Opera (qisman)

## 🔒 Xavfsizlik

- Camera faqat user ruxsati bilan ishlaydi
- Rasmlar faqat backend'ga yuboriladi
- Temporary fayllar o'chiriladi
- HTTPS ishlatish tavsiya etiladi

---

**🎉 Endi talabalar kamera orqali oson yuz yuklashlari mumkin!**

