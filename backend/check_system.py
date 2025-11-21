#!/usr/bin/env python3
"""
Tizim holatini tekshirish scripti
"""
import subprocess
import sys
import requests
import cv2
import os

def check_camera():
    """Kamerani tekshirish"""
    print("=" * 60)
    print("📷 KAMERA TEKSHIRISH")
    print("=" * 60)
    
    # Device'lar
    print("\n1. Kamera device'lar:")
    result = subprocess.run(['ls', '-la', '/dev/video*'], capture_output=True, text=True)
    if result.returncode == 0:
        print(result.stdout)
    else:
        print("❌ Kamera device'lar topilmadi")
    
    # Qaysi process ishlatayotgani
    print("\n2. Qaysi process kamerani ishlatayotgani:")
    result = subprocess.run(['lsof', '/dev/video0', '/dev/video1'], capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    else:
        print("✅ Kamera bo'sh (hech kim ishlatmayapti)")
    
    # OpenCV orqali test
    print("\n3. OpenCV orqali kamera test:")
    for i in range(3):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"   ✅ Kamera {i}: Ishlayapti (frame: {frame.shape if frame is not None else 'None'})")
            else:
                print(f"   ⚠️  Kamera {i}: Ochildi, lekin frame o'qib bo'lmadi")
            cap.release()
        else:
            print(f"   ❌ Kamera {i}: Ochilmadi")
    
    # Permission
    print("\n4. Permission tekshirish:")
    result = subprocess.run(['groups'], capture_output=True, text=True)
    groups = result.stdout.strip()
    if 'video' in groups:
        print(f"   ✅ Video group'da: {groups}")
    else:
        print(f"   ❌ Video group'da emas: {groups}")
        print("   💡 Qo'shish: sudo usermod -a -G video $USER")


def check_backend():
    """Backend tekshirish"""
    print("\n" + "=" * 60)
    print("🔧 BACKEND TEKSHIRISH")
    print("=" * 60)
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            print("✅ Backend ishlayapti: http://localhost:8000")
            print(f"   Response: {response.json()}")
        else:
            print(f"⚠️  Backend javob berdi, lekin status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Backend ishlamayapti (connection refused)")
        print("   💡 Ishga tushirish: cd backend && python3 -m uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Xatolik: {e}")


def check_frontend():
    """Frontend tekshirish"""
    print("\n" + "=" * 60)
    print("🎨 FRONTEND TEKSHIRISH")
    print("=" * 60)
    
    try:
        response = requests.get("http://localhost:3000", timeout=2)
        if response.status_code == 200:
            print("✅ Frontend ishlayapti: http://localhost:3000")
        else:
            print(f"⚠️  Frontend javob berdi, lekin status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Frontend ishlamayapti (connection refused)")
        print("   💡 Ishga tushirish: cd frontend && npm run dev")
    except Exception as e:
        print(f"❌ Xatolik: {e}")


def check_video_worker():
    """Video worker tekshirish"""
    print("\n" + "=" * 60)
    print("🎥 VIDEO WORKER TEKSHIRISH")
    print("=" * 60)
    
    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
    if 'video_worker' in result.stdout:
        print("✅ Video worker ishlayapti:")
        for line in result.stdout.split('\n'):
            if 'video_worker' in line:
                print(f"   {line}")
    else:
        print("❌ Video worker ishlamayapti")
        print("   💡 Ishga tushirish: cd backend && python3 -m video_worker.main")


def check_processes():
    """Barcha process'larni ko'rish"""
    print("\n" + "=" * 60)
    print("🔄 PROCESS'LAR")
    print("=" * 60)
    
    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
    relevant = []
    for line in result.stdout.split('\n'):
        if any(keyword in line.lower() for keyword in ['video', 'uvicorn', 'node', 'next', 'face']):
            relevant.append(line)
    
    if relevant:
        print("Topilgan process'lar:")
        for line in relevant[:10]:
            print(f"   {line}")
    else:
        print("❌ Hech qanday relevant process topilmadi")


def main():
    """Asosiy funksiya"""
    print("\n" + "=" * 60)
    print("🔍 TIZIM HOLATINI TEKSHIRISH")
    print("=" * 60)
    
    check_camera()
    check_backend()
    check_frontend()
    check_video_worker()
    check_processes()
    
    print("\n" + "=" * 60)
    print("✅ TEKSHIRISH YAKUNLANDI")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Bekor qilindi")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Xatolik: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

