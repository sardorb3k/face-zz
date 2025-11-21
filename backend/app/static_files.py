"""
Static file serving for images
"""
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from .config import IMAGES_DIR, DETECTED_FACES_DIR

def setup_static_files(app: FastAPI):
    """Setup static file serving for images"""
    # Student images
    app.mount("/static/student_images", StaticFiles(directory=str(IMAGES_DIR)), name="student_images")
    
    # Detected faces
    app.mount("/static/detected_faces", StaticFiles(directory=str(DETECTED_FACES_DIR)), name="detected_faces")

