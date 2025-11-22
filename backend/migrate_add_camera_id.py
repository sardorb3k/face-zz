#!/usr/bin/env python3
"""
Migration script to add camera_id column to face_verifications table
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import engine, SessionLocal
from sqlalchemy import text

def migrate():
    """Add camera_id column to face_verifications table"""
    db = SessionLocal()
    try:
        # Check if column already exists
        result = db.execute(text("""
            SELECT COUNT(*) as count 
            FROM pragma_table_info('face_verifications') 
            WHERE name = 'camera_id'
        """))
        exists = result.fetchone()[0] > 0
        
        if exists:
            print("✅ camera_id column already exists in face_verifications table")
            return
        
        # Add camera_id column
        print("Adding camera_id column to face_verifications table...")
        db.execute(text("""
            ALTER TABLE face_verifications 
            ADD COLUMN camera_id INTEGER 
            REFERENCES cameras(id) 
            ON DELETE SET NULL
        """))
        db.commit()
        print("✅ Successfully added camera_id column to face_verifications table")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error migrating database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate()

