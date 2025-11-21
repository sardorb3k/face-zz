#!/usr/bin/env python3
"""
Oddiy versiya - fayl orqali yuz yuklash
"""
import sys
import requests
import os
from pathlib import Path

API_URL = os.getenv("API_URL", "http://localhost:8000")

def create_student_and_upload(student_id, full_name, image_path, email=None, phone=None, course=None, group=None):
    """Talabani yaratish va yuz yuklash"""
    print("=" * 60)
    print("🎓 YANGI TALABA QO'SHISH")
    print("=" * 60)
    
    # Talabani yaratish
    print(f"\n👤 Talaba yaratilmoqda: {full_name} ({student_id})...")
    
    data = {
        "student_id": student_id,
        "full_name": full_name,
    }
    
    if email:
        data["email"] = email
    if phone:
        data["phone"] = phone
    if course:
        data["course"] = course
    if group:
        data["group"] = group
    
    try:
        response = requests.post(f"{API_URL}/api/students", json=data)
        
        if response.status_code != 200:
            error_msg = response.json().get('detail', 'Xatolik')
            print(f"❌ Xatolik: {error_msg}")
            return False
        
        student = response.json()
        print(f"✅ Talaba yaratildi! ID: {student['id']}")
        
        # Yuz rasmini yuklash
        print(f"\n📤 Yuz rasmi yuklanmoqda...")
        
        with open(image_path, 'rb') as f:
            files = {'file': (os.path.basename(image_path), f, 'image/jpeg')}
            data = {'student_id': student['id']}
            
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
                print("\n" + "=" * 60)
                print("✅ MUVAFFAQIYATLI!")
                print("=" * 60)
                return True
            else:
                error_msg = response.json().get('detail', 'Xatolik')
                print(f"❌ Xatolik: {error_msg}")
                return False
                
    except Exception as e:
        print(f"❌ Xatolik: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Foydalanish:")
        print(f"  {sys.argv[0]} <student_id> <full_name> <image_path> [email] [phone] [course] [group]")
        print("\nMisol:")
        print(f"  {sys.argv[0]} T2024001 'Ali Valiyev' image.jpg")
        print(f"  {sys.argv[0]} T2024001 'Ali Valiyev' image.jpg ali@example.com +998901234567")
        sys.exit(1)
    
    student_id = sys.argv[1]
    full_name = sys.argv[2]
    image_path = sys.argv[3]
    email = sys.argv[4] if len(sys.argv) > 4 else None
    phone = sys.argv[5] if len(sys.argv) > 5 else None
    course = sys.argv[6] if len(sys.argv) > 6 else None
    group = sys.argv[7] if len(sys.argv) > 7 else None
    
    if not Path(image_path).exists():
        print(f"❌ Rasm topilmadi: {image_path}")
        sys.exit(1)
    
    create_student_and_upload(student_id, full_name, image_path, email, phone, course, group)

