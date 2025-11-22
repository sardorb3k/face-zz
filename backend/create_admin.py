#!/usr/bin/env python3
"""
Create admin user script
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal, init_db
from app.models import User

def create_admin(username: str, password: str, email: str = None):
    """Create admin user"""
    db = SessionLocal()
    try:
        # Check if user exists
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            print(f"❌ User '{username}' already exists")
            return False
        
        # Create admin user
        admin = User(
            username=username,
            email=email,
            role="admin",
            is_active=True
        )
        admin.set_password(password)
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print(f"✅ Admin user '{username}' created successfully!")
        print(f"   ID: {admin.id}")
        print(f"   Role: {admin.role}")
        return True
    except Exception as e:
        print(f"❌ Error creating admin: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 create_admin.py <username> <password> [email]")
        print("\nExample:")
        print("  python3 create_admin.py admin admin123 admin@example.com")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    email = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Initialize database
    init_db()
    
    # Create admin
    create_admin(username, password, email)

