# Kamera Muammosini Tez Hal Qilish

## ❌ Muammo

Kameraga ulanib bo'lmadi - permission muammosi.

## ✅ Tez Yechim

### 1. Permission'ni tuzatish

```bash
cd services
./fix-camera-permissions.sh
```

### 2. Yangi terminal ochish yoki logout/login

```bash
# Yangi terminal oching yoki
logout
# keyin login qiling
```

### 3. Kamerani test qilish

```bash
cd services
./find-camera.sh
```

### 4. Video processor'ni ishga tushirish

```bash
./start-laptop-camera-cpu.sh
```

## 🔧 Qo'lda Yechim

Agar script ishlamasa:

```bash
# 1. User'ni video group'ga qo'shish
sudo usermod -a -G video $USER

# 2. Yangi terminal ochish yoki logout/login

# 3. Kamerani test qilish
cd services
./find-camera.sh
```

## ⚠️ Eslatma

Group o'zgarishlari keyin **yangi terminal ochish** yoki **logout/login qilish** kerak!

---

**💡 Eng keng tarqalgan muammo - user video group'ga tegishli emas!**




