"""
Video worker configuration
"""
import os
from pathlib import Path
from typing import List

# API endpoint
API_URL = os.getenv("API_URL", "http://localhost:8000")
ATTENDANCE_ENDPOINT = f"{API_URL}/api/attendance"

# Camera configuration
RTSP_CAMERAS = os.getenv("RTSP_CAMERAS", "").split(",") if os.getenv("RTSP_CAMERAS") else []
RTSP_CAMERAS = [url.strip() for url in RTSP_CAMERAS if url.strip()]

LAPTOP_CAMERA_INDEX = int(os.getenv("LAPTOP_CAMERA_INDEX", "0"))
USE_LAPTOP_CAMERA = os.getenv("USE_LAPTOP_CAMERA", "true").lower() == "true"

# Face detection/recognition
FACE_DETECTION_THRESHOLD = float(os.getenv("FACE_DETECTION_THRESHOLD", "0.5"))
FACE_RECOGNITION_THRESHOLD = float(os.getenv("FACE_RECOGNITION_THRESHOLD", "0.4"))
MODEL_NAME = os.getenv("MODEL_NAME", "buffalo_l")
USE_GPU = os.getenv("USE_GPU", "false").lower() == "true"
MODEL_DIR = Path(os.getenv("MODEL_DIR", "./models"))

# DeepSORT
DEEPSORT_ENABLED = os.getenv("DEEPSORT_ENABLED", "true").lower() == "true"

# Processing settings
FRAME_SKIP = int(os.getenv("FRAME_SKIP", "2"))  # Process every Nth frame
DETECTED_FACES_DIR = Path(os.getenv("DETECTED_FACES_DIR", "./data/detected_faces"))
DETECTED_FACES_DIR.mkdir(exist_ok=True, parents=True)

# Duplicate prevention
DUPLICATE_PREVENTION_WINDOW_SECONDS = int(os.getenv("DUPLICATE_PREVENTION_WINDOW_SECONDS", "60"))

# Camera reconnection
RECONNECT_DELAY = int(os.getenv("RECONNECT_DELAY", "5"))  # seconds
MAX_RECONNECT_ATTEMPTS = int(os.getenv("MAX_RECONNECT_ATTEMPTS", "10"))

