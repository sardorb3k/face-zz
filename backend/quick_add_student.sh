#!/bin/bash
# Tezkor talaba qo'shish scripti

echo "🔄 Video worker ni to'xtatmoqda..."
pkill -f "video_worker.main" 2>/dev/null
sleep 2

echo "✅ Video worker to'xtatildi"
echo ""
echo "📝 Talaba qo'shish scriptini ishga tushirish..."
echo ""

cd "$(dirname "$0")"
python3 add_student_camera.py

echo ""
echo "🔄 Video worker ni qayta ishga tushirishni xohlaysizmi? (y/n)"
read -r answer

if [ "$answer" = "y" ] || [ "$answer" = "Y" ]; then
    echo "🔄 Video worker ishga tushirilmoqda..."
    python3 -m video_worker.main &
    echo "✅ Video worker ishga tushirildi (background)"
fi

