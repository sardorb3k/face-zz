#!/usr/bin/env python3
"""
Kamera orqali yangi talaba qo'shish va embedding yaratish scripti
"""
import cv2
import sys
import requests
import json
from pathlib import Path
import os

# Backend API URL
API_URL = os.getenv("API_URL", "http://localhost:8000")

def detect_face_from_camera(camera_index=None):
    """Kameradan yuzni aniqlash"""
    print("📷 Kamerani ochmoqda...")
    
    # Kamerani topish
    cap = None
    if camera_index is not None:
        cap = cv2.VideoCapture(camera_index)
        if cap.isOpened():
            print(f"✅ Kamera {camera_index} ochildi")
        else:
            cap.release()
            cap = None
    else:
        # Avtomatik kamera topish
        for idx in range(3):
            test_cap = cv2.VideoCapture(idx)
            if test_cap.isOpened():
                # Test frame o'qish
                ret, _ = test_cap.read()
                if ret:
                    cap = test_cap
                    print(f"✅ Kamera {idx} topildi va ochildi")
                    break
                else:
                    test_cap.release()
            else:
                test_cap.release()
    
    if cap is None or not cap.isOpened():
        print("❌ Xatolik: Kameraga ulanib bo'lmadi")
        print("💡 Tekshirish:")
        print("   1. Kamera ulanganligini tekshiring: ls -la /dev/video*")
        print("   2. Permission tekshiring: groups $USER")
        print("   3. Video group'ga qo'shing: sudo usermod -a -G video $USER")
        print("   4. Boshqa dastur kamerani ishlatayotgan bo'lishi mumkin")
        print("   5. Boshqa index sinab ko'ring: python3 add_student_camera.py --camera 1")
        return None
    
    print("✅ Kamera ochildi")
    print("\n📸 Yuzni aniqlash uchun kameraga qarang...")
    print("   'SPACE' - rasmni saqlash")
    print("   'q' - chiqish")
    
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Frame o'qib bo'lmadi")
            break
        
        # Yuzni aniqlash
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        # Yuzni chizish
        frame_with_face = frame.copy()
        face_detected = False
        
        for (x, y, w, h) in faces:
            cv2.rectangle(frame_with_face, (x, y), (x+w, y+h), (0, 255, 0), 2)
            face_detected = True
        
        # Ko'rsatish
        cv2.imshow('Yuzni aniqlash - SPACE: saqlash, q: chiqish', frame_with_face)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            print("\n❌ Bekor qilindi")
            break
        elif key == ord(' '):  # SPACE
            if face_detected:
                # Yuzni kesib olish
                if len(faces) > 0:
                    x, y, w, h = faces[0]
                    # Biroz margin qo'shish
                    margin = 20
                    x = max(0, x - margin)
                    y = max(0, y - margin)
                    w = min(frame.shape[1] - x, w + 2 * margin)
                    h = min(frame.shape[0] - y, h + 2 * margin)
                    face_image = frame[y:y+h, x:x+w]
                    
                    cap.release()
                    cv2.destroyAllWindows()
                    return face_image
                else:
                    print("⚠️  Yuz topilmadi, qayta urinib ko'ring")
            else:
                print("⚠️  Yuz topilmadi, qayta urinib ko'ring")
    
    cap.release()
    cv2.destroyAllWindows()
    return None


def save_temp_image(face_image, temp_dir="temp_images"):
    """Vaqtinchalik rasmni saqlash"""
    temp_path = Path(temp_dir)
    temp_path.mkdir(exist_ok=True)
    
    import uuid
    filename = f"temp_{uuid.uuid4()}.jpg"
    filepath = temp_path / filename
    
    cv2.imwrite(str(filepath), face_image)
    return str(filepath)


def create_student(student_id, full_name, email=None, phone=None, course=None, group=None):
    """Yangi talaba yaratish"""
    print(f"\n👤 Talaba yaratilmoqda: {full_name} ({student_id})...")
    
    data = {
        "student_id": student_id,
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "course": course,
        "group": group
    }
    
    # None qiymatlarni olib tashlash
    data = {k: v for k, v in data.items() if v is not None}
    
    try:
        response = requests.post(f"{API_URL}/api/students", json=data)
        
        if response.status_code == 200:
            student = response.json()
            print(f"✅ Talaba yaratildi! ID: {student['id']}")
            return student
        else:
            error_msg = response.json().get('detail', 'Xatolik')
            print(f"❌ Xatolik: {error_msg}")
            return None
    except Exception as e:
        print(f"❌ Xatolik: {e}")
        return None


def upload_face_image(student_id, image_path):
    """Yuz rasmini yuklash va embedding yaratish"""
    print(f"\n📤 Yuz rasmi yuklanmoqda...")
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': (os.path.basename(image_path), f, 'image/jpeg')}
            data = {'student_id': student_id}
            
            response = requests.post(
                f"{API_URL}/api/upload/face",
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Yuz rasmi yuklandi!")
                if result.get('embedding_created'):
                    print(f"✅ Embedding yaratildi!")
                else:
                    print(f"⚠️  Embedding yaratilmadi")
                return True
            else:
                error_msg = response.json().get('detail', 'Xatolik')
                print(f"❌ Xatolik: {error_msg}")
                return False
    except Exception as e:
        print(f"❌ Xatolik: {e}")
        return False
    finally:
        # Vaqtinchalik faylni o'chirish
        try:
            os.remove(image_path)
        except:
            pass


def main():
    """Asosiy funksiya"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Kamera orqali yangi talaba qo\'shish')
    parser.add_argument('--camera', type=int, help='Kamera index (0, 1, 2, ...)')
    args = parser.parse_args()
    
    print("=" * 60)
    print("🎓 YANGI TALABA QO'SHISH (Kamera orqali)")
    print("=" * 60)
    
    # Talaba ma'lumotlarini so'rash
    print("\n📝 Talaba ma'lumotlarini kiriting:")
    student_id = input("Talaba ID: ").strip()
    if not student_id:
        print("❌ Talaba ID kiritilishi shart!")
        return
    
    full_name = input("Ism Familiya: ").strip()
    if not full_name:
        print("❌ Ism Familiya kiritilishi shart!")
        return
    
    email = input("Email (ixtiyoriy): ").strip() or None
    phone = input("Telefon (ixtiyoriy): ").strip() or None
    course = input("Kurs (ixtiyoriy): ").strip() or None
    group = input("Guruh (ixtiyoriy): ").strip() or None
    
    # Kameradan yuzni aniqlash
    face_image = detect_face_from_camera(camera_index=args.camera)
    
    if face_image is None:
        print("\n❌ Yuz aniqlanmadi yoki bekor qilindi")
        return
    
    print(f"\n✅ Yuz aniqlandi! O'lcham: {face_image.shape}")
    
    # Talabani yaratish
    student = create_student(student_id, full_name, email, phone, course, group)
    
    if student is None:
        print("\n❌ Talaba yaratilmadi")
        return
    
    # Rasmni saqlash
    temp_image_path = save_temp_image(face_image)
    
    # Yuz rasmini yuklash
    success = upload_face_image(student['id'], temp_image_path)
    
    if success:
        print("\n" + "=" * 60)
        print("✅ MUVAFFAQIYATLI!")
        print("=" * 60)
        print(f"Talaba: {full_name} ({student_id})")
        print(f"ID: {student['id']}")
        print(f"Yuz rasmi yuklandi va embedding yaratildi")
        print("\n💡 Qo'shimcha yuz rasmlari yuklash uchun:")
        print(f"   - Frontend orqali: http://localhost:3000")
        print(f"   - API orqali: POST {API_URL}/api/upload/face")
    else:
        print("\n❌ Yuz rasmi yuklanmadi")


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

