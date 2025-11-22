"""
Attendance manager with duplicate prevention
"""
import requests
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
from .config import ATTENDANCE_ENDPOINT, DUPLICATE_PREVENTION_WINDOW_SECONDS, DETECTED_FACES_DIR
import cv2
import uuid
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.database import SessionLocal
from app.models import Student

logger = logging.getLogger(__name__)


class AttendanceManager:
    """Manages attendance logging with duplicate prevention"""
    
    def __init__(self):
        # Track last attendance per (student_id, camera_id)
        self.last_attendance: Dict[tuple, datetime] = {}
        self.window_seconds = DUPLICATE_PREVENTION_WINDOW_SECONDS
    
    def can_log_attendance(self, student_id: int, camera_id: int) -> bool:
        """
        Check if attendance can be logged (not duplicate)
        
        Args:
            student_id: Student ID
            camera_id: Camera ID
            
        Returns:
            True if attendance can be logged, False if duplicate
        """
        key = (student_id, camera_id)
        now = datetime.utcnow()
        
        if key in self.last_attendance:
            last_time = self.last_attendance[key]
            time_diff = (now - last_time).total_seconds()
            
            if time_diff < self.window_seconds:
                logger.debug(f"Duplicate prevention: Student {student_id} on camera {camera_id} logged {time_diff:.1f}s ago")
                return False
        
        return True
    
    def log_attendance(
        self,
        student_id: int,
        camera_id: int,
        confidence: float,
        track_id: Optional[int] = None,
        face_image: Optional[any] = None
    ) -> bool:
        """
        Log attendance via API
        
        Args:
            student_id: Student ID
            camera_id: Camera ID
            confidence: Recognition confidence
            track_id: DeepSORT track ID
            face_image: Optional face image to save
            
        Returns:
            True if logged successfully, False otherwise
        """
        # Check duplicate prevention
        if not self.can_log_attendance(student_id, camera_id):
            return False
        
        # Save face image if provided
        image_path = None
        if face_image is not None:
            try:
                image_filename = f"{student_id}_{camera_id}_{uuid.uuid4()}.jpg"
                image_path = str(DETECTED_FACES_DIR / image_filename)
                cv2.imwrite(image_path, face_image)
            except Exception as e:
                logger.error(f"Error saving face image: {e}")
        
        # Call API
        try:
            payload = {
                "student_id": student_id,
                "camera_id": camera_id,
                "confidence": float(confidence),
                "track_id": track_id,
                "image_path": image_path
            }
            
            response = requests.post(ATTENDANCE_ENDPOINT, json=payload, timeout=5)
            
            if response.status_code == 200:
                # Update last attendance time
                key = (student_id, camera_id)
                self.last_attendance[key] = datetime.utcnow()
                
                # Get student name from database
                student_name = None
                try:
                    db = SessionLocal()
                    student = db.query(Student).filter(Student.id == student_id).first()
                    if student:
                        student_name = student.full_name
                    db.close()
                except Exception as e:
                    logger.debug(f"Could not fetch student name: {e}")
                
                # Console log for successful attendance logging
                student_info = f"{student_name} (ID: {student_id})" if student_name else f"Student ID {student_id}"
                log_message = f"✅ BU TALABA DAVOMOTI SAQLANDI: {student_info} (camera: {camera_id}, confidence: {confidence:.3f})"
                logger.info(log_message)
                print(log_message)
                return True
            else:
                logger.error(f"Failed to log attendance: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error calling attendance API: {e}")
            return False
    
    def cleanup_old_records(self):
        """Clean up old attendance records from memory"""
        now = datetime.utcnow()
        keys_to_remove = []
        
        for key, last_time in self.last_attendance.items():
            time_diff = (now - last_time).total_seconds()
            if time_diff > self.window_seconds * 2:  # Keep records for 2x window
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.last_attendance[key]

