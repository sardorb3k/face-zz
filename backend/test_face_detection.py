#!/usr/bin/env python3
"""
Rasmda yuzni aniqlashni test qilish
"""
import sys
import cv2
from pathlib import Path

def test_face_detection(image_path):
    """Rasmda yuzni aniqlashni test qilish"""
    print(f"📸 Rasmni yuklanmoqda: {image_path}")
    
    if not Path(image_path).exists():
        print(f"❌ Rasm topilmadi: {image_path}")
        return False
    
    # Rasmni yuklash
    image = cv2.imread(image_path)
    if image is None:
        print(f"❌ Rasm yuklanmadi (formati noto'g'ri bo'lishi mumkin)")
        return False
    
    print(f"✅ Rasm yuklandi: {image.shape}")
    
    # OpenCV CascadeClassifier orqali test
    print("\n1. OpenCV CascadeClassifier orqali test:")
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    if len(faces) > 0:
        print(f"   ✅ {len(faces)} ta yuz aniqlandi (OpenCV)")
        for i, (x, y, w, h) in enumerate(faces):
            print(f"      Yuz {i+1}: x={x}, y={y}, w={w}, h={h}")
    else:
        print("   ❌ Yuz topilmadi (OpenCV)")
    
    # InsightFace orqali test
    print("\n2. InsightFace orqali test:")
    try:
        import insightface
        app = insightface.app.FaceAnalysis(name="buffalo_l", providers=['CPUExecutionProvider'])
        app.prepare(ctx_id=0, det_size=(640, 640))
        
        faces_if = app.get(image)
        
        if faces_if and len(faces_if) > 0:
            print(f"   ✅ {len(faces_if)} ta yuz aniqlandi (InsightFace)")
            for i, face in enumerate(faces_if):
                bbox = face.bbox.astype(int)
                print(f"      Yuz {i+1}: bbox={bbox}, confidence={face.det_score:.3f}")
        else:
            print("   ❌ Yuz topilmadi (InsightFace)")
    except Exception as e:
        print(f"   ⚠️  InsightFace test qilishda xatolik: {e}")
    
    # Rasmni ko'rsatish (agar yuz topilsa)
    if len(faces) > 0:
        print("\n💡 Rasmda yuz aniqlandi! Rasmni ko'rish uchun 'q' bosing")
        for (x, y, w, h) in faces:
            cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        cv2.imshow('Face Detection Test', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    return len(faces) > 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Foydalanish:")
        print(f"  {sys.argv[0]} <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    test_face_detection(image_path)

