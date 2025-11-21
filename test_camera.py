#!/usr/bin/env python3
"""
Kamerani test qilish skripti
"""
import cv2
import sys

def test_camera(index=0):
    """Kamerani test qilish"""
    print(f"Kamera {index} ni test qilmoqda...")
    
    cap = cv2.VideoCapture(index)
    
    if not cap.isOpened():
        print(f"❌ Kamera {index} ochilmadi")
        return False
    
    print(f"✅ Kamera {index} ochildi")
    
    # Bir necha frame o'qish
    for i in range(5):
        ret, frame = cap.read()
        if ret:
            print(f"  Frame {i+1}: {frame.shape if frame is not None else 'None'}")
        else:
            print(f"  Frame {i+1}: O'qib bo'lmadi")
            break
    
    cap.release()
    print(f"✅ Kamera {index} test muvaffaqiyatli")
    return True

if __name__ == "__main__":
    index = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    test_camera(index)

