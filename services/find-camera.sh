#!/bin/bash

# Kamerani topish va test qilish scripti

echo "=========================================="
echo "Kamera Tekshirish"
echo "=========================================="

# Python tekshirish
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 topilmadi!"
    exit 1
fi

# OpenCV tekshirish
python3 << 'EOF'
import cv2
import sys

print("🔍 Mavjud kameralarni tekshirish...")
print("")

# 0 dan 10 gacha kameralarni tekshirish
found_cameras = []

for i in range(10):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        # Kameradan frame o'qishga urinish
        ret, frame = cap.read()
        if ret:
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            backend = cap.getBackendName()
            
            found_cameras.append({
                'index': i,
                'width': width,
                'height': height,
                'fps': fps,
                'backend': backend
            })
            
            print(f"✅ Kamera topildi: Index {i}")
            print(f"   Resolution: {width}x{height}")
            print(f"   FPS: {fps}")
            print(f"   Backend: {backend}")
            print("")
        cap.release()

if not found_cameras:
    print("❌ Hech qanday kamera topilmadi!")
    print("")
    print("💡 Yechimlar:")
    print("   1. Kamera ulanganligini tekshiring")
    print("   2. Kamera boshqa dastur tomonidan ishlatilmayaptimi?")
    print("   3. Kamera driver'lari o'rnatilganmi?")
    print("   4. lsusb | grep -i camera  # USB kameralarni ko'rish")
    print("   5. v4l2-ctl --list-devices  # Video device'larni ko'rish")
    sys.exit(1)
else:
    print(f"✅ Jami {len(found_cameras)} ta kamera topildi!")
    print("")
    print("📋 Foydalanish:")
    print(f"   ./start-laptop-camera-cpu.sh  # Birinchi kamera (index {found_cameras[0]['index']})")
    print("")
    print("   yoki to'g'ridan-to'g'ri:")
    print(f"   export CAMERA_INDEX={found_cameras[0]['index']}")
    print("   ./start-laptop-camera-cpu.sh")
    sys.exit(0)
EOF





