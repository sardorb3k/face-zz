"""
SQLAlchemy models for the attendance system
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, BLOB, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import numpy as np


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

