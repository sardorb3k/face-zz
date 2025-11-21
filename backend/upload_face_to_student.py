#!/usr/bin/env python3
"""
Mavjud talabaga yuz rasmini yuklash
"""
import sys
import requests
import os
from pathlib import Path

API_URL = os.getenv("API_URL", "http://localhost:8000")

def upload_face_to_student(student_id_or_db_id, image_path):
    """Mavjud talabaga yuz rasmini yuklash"""
    
    # Talabani topish
    try:
        response = requests.get(f"{API_URL}/api/students")
        students = response.json()
        
        # ID yoki student_id bo'yicha qidirish
        student = None
        if isinstance(student_id_or_db_id, int) or student_id_or_db_id.isdigit():
            # Database ID
            student = next((s for s in students if s['id'] == int(student_id_or_db_id)), None)
        else:
            # Student ID
            student = next((s for s in students if s['student_id'] == student_id_or_db_id), None)
        
        if not student:
            print(f"❌ Talaba topilmadi: {student_id_or_db_id}")
            print("\nMavjud talabalar:")
            for s in students[:10]:
                print(f"  ID: {s['id']}, Student ID: {s['student_id']}, Name: {s['full_name']}")
            return False
        
        print(f"✅ Talaba topildi: {student['full_name']} (ID: {student['id']}, Student ID: {student['student_id']})")
        
    except Exception as e:
        print(f"❌ Xatolik: {e}")
        return False
    
    if not Path(image_path).exists():
        print(f"❌ Rasm topilmadi: {image_path}")
        return False
    
    print(f"\n📤 Yuz rasmi yuklanmoqda: {image_path}")
    
    try:
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
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Foydalanish:")
        print(f"  {sys.argv[0]} <student_id_or_db_id> <image_path>")
        print("\nMisol:")
        print(f"  {sys.argv[0]} 2 image.png")
        print(f"  {sys.argv[0]} T2024001 image.png")
        sys.exit(1)
    
    student_id = sys.argv[1]
    image_path = sys.argv[2]
    
    upload_face_to_student(student_id, image_path)

