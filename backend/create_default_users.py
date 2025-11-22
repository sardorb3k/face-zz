#!/usr/bin/env python3
"""
Create default users (admin and student) for testing
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal, init_db
from app.models import User, Student

def create_default_users():
    """Create default admin and student users"""
    db = SessionLocal()
    try:
        # Initialize database
        init_db()
        
        # Create default admin
        admin_username = "admin"
        admin_password = "admin123"
        admin_email = "admin@face-r.local"
        
        existing_admin = db.query(User).filter(User.username == admin_username).first()
        if existing_admin:
            print(f"⚠️  Admin user '{admin_username}' already exists (ID: {existing_admin.id})")
        else:
            admin = User(
                username=admin_username,
                email=admin_email,
                role="admin",
                is_active=True
            )
            admin.set_password(admin_password)
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print(f"✅ Admin user yaratildi!")
            print(f"   Username: {admin_username}")
            print(f"   Password: {admin_password}")
            print(f"   Email: {admin_email}")
            print(f"   ID: {admin.id}")
        
        # Create default student
        student_username = "student"
        student_password = "student123"
        student_email = "student@face-r.local"
        
        # First create a student record
        existing_student = db.query(Student).filter(Student.student_id == "ST001").first()
        if not existing_student:
            student_record = Student(
                student_id="ST001",
                full_name="Test Student",
                email=student_email,
                course="Test Course",
                group="Test Group",
                is_active=True
            )
            db.add(student_record)
            db.commit()
            db.refresh(student_record)
            print(f"\n✅ Test talaba yaratildi!")
            print(f"   Student ID: {student_record.student_id}")
            print(f"   Full Name: {student_record.full_name}")
            student_id = student_record.id
        else:
            print(f"\n⚠️  Test talaba allaqachon mavjud (ID: {existing_student.id})")
            student_id = existing_student.id
        
        # Create student user
        existing_student_user = db.query(User).filter(User.username == student_username).first()
        if existing_student_user:
            print(f"⚠️  Student user '{student_username}' already exists (ID: {existing_student_user.id})")
        else:
            student_user = User(
                username=student_username,
                email=student_email,
                role="student",
                student_id=student_id,
                is_active=True
            )
            student_user.set_password(student_password)
            db.add(student_user)
            db.commit()
            db.refresh(student_user)
            print(f"\n✅ Student user yaratildi!")
            print(f"   Username: {student_username}")
            print(f"   Password: {student_password}")
            print(f"   Email: {student_email}")
            print(f"   Student ID: {student_id}")
            print(f"   User ID: {student_user.id}")
        
        print("\n" + "="*50)
        print("DEFAULT LOGIN MA'LUMOTLARI:")
        print("="*50)
        print("\n🔴 ADMIN:")
        print(f"   URL: http://localhost:3000/login")
        print(f"   Username: {admin_username}")
        print(f"   Password: {admin_password}")
        print("\n🟢 STUDENT:")
        print(f"   URL: http://localhost:3000/login")
        print(f"   Username: {student_username}")
        print(f"   Password: {student_password}")
        print("\n" + "="*50)
        
        return True
    except Exception as e:
        print(f"❌ Xatolik: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("Default user'lar yaratilmoqda...\n")
    success = create_default_users()
    if success:
        print("\n✅ Barcha user'lar muvaffaqiyatli yaratildi!")
    else:
        print("\n❌ Xatolik yuz berdi!")
        sys.exit(1)

