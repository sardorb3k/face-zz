"""
SQLAlchemy models for the attendance system
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, BLOB, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.sqlite import JSON
from .database import Base
import numpy as np
import hashlib
import secrets


class Student(Base):
    """Student information"""
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, unique=True, index=True, nullable=False)  # University ID
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    course = Column(String, nullable=True)
    group = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    images = relationship("StudentImage", back_populates="student", cascade="all, delete-orphan")
    embeddings = relationship("StudentEmbedding", back_populates="student", cascade="all, delete-orphan")
    attendance_logs = relationship("AttendanceLog", back_populates="student")


class StudentImage(Base):
    """Student face images (1-5 images per student)"""
    __tablename__ = "student_images"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    image_path = Column(String, nullable=False)  # Path to stored image file
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    student = relationship("Student", back_populates="images")


class StudentEmbedding(Base):
    """Averaged face embeddings for students"""
    __tablename__ = "student_embeddings"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), unique=True, nullable=False)
    embedding = Column(BLOB, nullable=False)  # 512-dim numpy array as bytes
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    student = relationship("Student", back_populates="embeddings")
    
    def get_embedding_array(self) -> np.ndarray:
        """Convert BLOB to numpy array"""
        return np.frombuffer(self.embedding, dtype=np.float32)
    
    def set_embedding_array(self, embedding: np.ndarray):
        """Convert numpy array to BLOB"""
        self.embedding = embedding.astype(np.float32).tobytes()


class Camera(Base):
    """Camera configuration"""
    __tablename__ = "cameras"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    rtsp_url = Column(String, nullable=True)  # RTSP URL for IP cameras
    camera_type = Column(String, nullable=False)  # 'rtsp' or 'laptop'
    camera_index = Column(Integer, nullable=True)  # For laptop cameras (0, 1, etc.)
    is_active = Column(Boolean, default=True)
    location = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    attendance_logs = relationship("AttendanceLog", back_populates="camera")


class AttendanceLog(Base):
    """Attendance records"""
    __tablename__ = "attendance_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="SET NULL"), nullable=True)
    camera_id = Column(Integer, ForeignKey("cameras.id", ondelete="SET NULL"), nullable=True)
    detected_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    confidence = Column(Float, nullable=True)  # Recognition confidence (cosine similarity)
    track_id = Column(Integer, nullable=True)  # DeepSORT track ID
    image_path = Column(String, nullable=True)  # Path to detected face image
    
    # Relationships
    student = relationship("Student", back_populates="attendance_logs")
    camera = relationship("Camera", back_populates="attendance_logs")


class User(Base):
    """Users for authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="student")  # 'student' or 'admin'
    student_id = Column(Integer, ForeignKey("students.id", ondelete="SET NULL"), nullable=True)  # For student users
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    student = relationship("Student", foreign_keys=[student_id])
    
    def set_password(self, password: str):
        """Set password hash"""
        # Simple password hashing using SHA256 + salt
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        self.hashed_password = f"{salt}:{password_hash}"
    
    def check_password(self, password: str) -> bool:
        """Check password"""
        if not self.hashed_password or ':' not in self.hashed_password:
            return False
        salt, stored_hash = self.hashed_password.split(':', 1)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return password_hash == stored_hash


class FaceVerification(Base):
    """Face verification requests"""
    __tablename__ = "face_verifications"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    camera_id = Column(Integer, ForeignKey("cameras.id", ondelete="SET NULL"), nullable=True)  # Camera used for verification
    image_path = Column(String, nullable=False)
    verification_status = Column(String, nullable=False, default="pending")  # 'pending', 'approved', 'rejected'
    confidence = Column(Float, nullable=True)  # Verification confidence
    reviewed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)  # Admin who reviewed
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)  # Admin notes
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    student = relationship("Student")
    camera = relationship("Camera")
    reviewer = relationship("User", foreign_keys=[reviewed_by])


class SystemConfig(Base):
    """System configuration"""
    __tablename__ = "system_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, nullable=False)
    value = Column(Text, nullable=True)  # JSON string or plain text
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

