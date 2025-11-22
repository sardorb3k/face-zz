# Kamera Muammosini Hal Qilish

## ❌ Muammo

```
[ WARN:0@5.479] global cap_v4l.cpp:914 open VIDEOIO(V4L2:/dev/video0): can't open camera by index
[ERROR:0@5.480] global obsensor_uvc_stream_channel.cpp:163 getStreamChannelGroup Camera index out of range
Xatolik: Kameraga ulanib bo'lmadi (Index: 0)
```

## 🔍 Tekshirish

### 1. Kamera Device'larini Tekshirish

```bash
ls -la /dev/video*
```

Agar device'lar mavjud bo'lsa, lekin ochib bo'lmasa, permission muammosi bo'lishi mumkin.

### 2. Permission Tekshirish

```bash
groups $USER
```

Agar `video` group ko'rinmasa, user video group'ga qo'shilishi kerak.

## ✅ Yechimlar

### Variant 1: User'ni video group'ga qo'shish (Tavsiya)

```bash
# User'ni video group'ga qo'shish
sudo usermod -a -G video $USER

# Keyin logout/login qilish yoki yangi terminal ochish
# yoki
newgrp video
```

### Variant 2: Sudo orqali ishga tushirish

```bash
# Sudo orqali ishga tushirish (tavsiya etilmaydi)
sudo python -m video_processor.main --camera-index 0 --location laptop_camera --no-display
```

### Variant 3: Permission'ni o'zgartirish (Xavfsizlik nuqtai nazaridan tavsiya etilmaydi)

```bash
# Device permission'ni o'zgartirish
sudo chmod 666 /dev/video0
sudo chmod 666 /dev/video1
```

### Variant 4: Kamera boshqa dastur tomonidan ishlatilmoqda

```bash
# Qaysi dastur kamerani ishlatayotganini topish
lsof /dev/video0
lsof /dev/video1

# Dasturni to'xtatish
kill <PID>
```

## 🔧 Qo'shimcha Tekshirish

### Kamera Device'larini Ko'rish

```bash
# Video device'lar
ls -la /dev/video*

# USB kameralar
lsusb | grep -i camera

# Video device ma'lumotlari (v4l2-utils o'rnatilgan bo'lsa)
sudo dnf install v4l-utils  # Fedora
sudo apt-get install v4l-utils  # Ubuntu/Debian

v4l2-ctl --list-devices
```

### OpenCV orqali Test

```bash
cd services
./find-camera.sh
```

## 📋 To'liq Yechim

### 1. User'ni video group'ga qo'shish

```bash
sudo usermod -a -G video $USER
```

### 2. Logout/Login yoki yangi terminal

```bash
# Yangi terminal ochish yoki
newgrp video
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

## ⚠️ Eslatmalar

1. **Permission** - Eng keng tarqalgan muammo
2. **Group** - User `video` group'ga tegishli bo'lishi kerak
3. **Logout/Login** - Group o'zgarishlari keyin logout/login qilish kerak
4. **Boshqa dastur** - Kamera boshqa dastur tomonidan ishlatilayotgan bo'lishi mumkin

## 🎯 Tekshirish

```bash
# 1. User group'larini tekshirish
groups $USER

# 2. Kamera device'larini tekshirish
ls -la /dev/video*

# 3. Kamera boshqa dastur tomonidan ishlatilayotganini tekshirish
lsof /dev/video0

# 4. Kamerani test qilish
cd services
./find-camera.sh
```

---

**💡 Eng keng tarqalgan muammo - user video group'ga tegishli emas!**





