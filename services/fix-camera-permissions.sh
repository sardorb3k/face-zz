#!/bin/bash

# Kamera permission muammosini hal qilish scripti

echo "=========================================="
echo "Kamera Permission Muammosini Hal Qilish"
echo "=========================================="

# User'ni video group'ga qo'shish
echo "1️⃣  User'ni video group'ga qo'shish..."
echo "   (Sudo parol so'rashi mumkin)"

if sudo usermod -a -G video $USER; then
    echo "✅ User video group'ga qo'shildi!"
else
    echo "❌ Xatolik: User'ni video group'ga qo'shib bo'lmadi"
    exit 1
fi

echo ""
echo "2️⃣  Group o'zgarishlarini qo'llash..."
echo "   (Yangi terminal ochish yoki logout/login qilish kerak)"

# Yangi group'ni faollashtirish
if command -v newgrp &> /dev/null; then
    echo "   newgrp video buyrug'i ishlatilmoqda..."
    echo "   (Bu yangi shell yaratadi)"
    echo ""
    echo "💡 Keyingi qadamlar:"
    echo "   1. Yangi terminal oching"
    echo "   2. yoki logout/login qiling"
    echo "   3. yoki quyidagi buyruqni ishlating:"
    echo "      newgrp video"
    echo ""
    echo "   4. Keyin kamerani test qiling:"
    echo "      cd services"
    echo "      ./find-camera.sh"
else
    echo "   newgrp topilmadi"
    echo ""
    echo "💡 Keyingi qadamlar:"
    echo "   1. Yangi terminal oching"
    echo "   2. yoki logout/login qiling"
    echo "   3. Keyin kamerani test qiling:"
    echo "      cd services"
    echo "      ./find-camera.sh"
fi

echo ""
echo "=========================================="
echo "✅ Sozlash yakunlandi!"
echo "=========================================="
echo ""
echo "📋 Keyingi qadamlar:"
echo "   1. Yangi terminal oching yoki logout/login qiling"
echo "   2. Kamerani test qiling:"
echo "      cd services"
echo "      ./find-camera.sh"
echo "   3. Video processor'ni ishga tushiring:"
echo "      ./start-laptop-camera-cpu.sh"
echo ""




