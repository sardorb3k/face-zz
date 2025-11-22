"""
Configuration settings
"""
import os
from pathlib import Path
from typing import List

# Base directories
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR / "data"))
MODEL_DIR = Path(os.getenv("MODEL_DIR", BASE_DIR / "models"))
DB_DIR = Path(os.getenv("DB_DIR", DATA_DIR))
IMAGES_DIR = DATA_DIR / "student_images"
DETECTED_FACES_DIR = DATA_DIR / "detected_faces"

# Create directories
DATA_DIR.mkdir(exist_ok=True, parents=True)
MODEL_DIR.mkdir(exist_ok=True, parents=True)
DB_DIR.mkdir(exist_ok=True, parents=True)
IMAGES_DIR.mkdir(exist_ok=True, parents=True)
DETECTED_FACES_DIR.mkdir(exist_ok=True, parents=True)

# Database
DATABASE_URL = f"sqlite:///{DB_DIR / 'attendance.db'}"

# Face Recognition
FACE_RECOGNITION_THRESHOLD = float(os.getenv("FACE_RECOGNITION_THRESHOLD", "0.4"))
MODEL_NAME = os.getenv("MODEL_NAME", "buffalo_l")
USE_GPU = os.getenv("USE_GPU", "false").lower() == "true"

# API Settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_URL = os.getenv("API_URL", f"http://localhost:{API_PORT}")

# Video Worker Settings
# Note: RTSP cameras are now configured via database (admin panel)
# RTSP_CAMERAS env variable is deprecated and no longer used
# RTSP_CAMERAS = os.getenv("RTSP_CAMERAS", "").split(",") if os.getenv("RTSP_CAMERAS") else []
# RTSP_CAMERAS = [url.strip() for url in RTSP_CAMERAS if url.strip()]

# Laptop camera (optional, disabled by default)
USE_LAPTOP_CAMERA = os.getenv("USE_LAPTOP_CAMERA", "false").lower() == "true"
LAPTOP_CAMERA_INDEX = int(os.getenv("LAPTOP_CAMERA_INDEX", "0")) if USE_LAPTOP_CAMERA else None

# Duplicate prevention
DUPLICATE_PREVENTION_WINDOW_SECONDS = int(os.getenv("DUPLICATE_PREVENTION_WINDOW_SECONDS", "60"))  # 1 minute

# DeepSORT
DEEPSORT_ENABLED = os.getenv("DEEPSORT_ENABLED", "true").lower() == "true"

# CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

