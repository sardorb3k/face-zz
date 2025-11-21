"""
Face recognizer using ArcFace
"""
import sys
from pathlib import Path
import logging

# Add parent directory to path to import app services
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.face_recognition import FaceRecognitionService
from app.services.embedding_service import EmbeddingService
from app.database import SessionLocal
from typing import Optional, Tuple
import numpy as np

logger = logging.getLogger(__name__)


class FaceRecognizer:
    """Face recognition using ArcFace"""
    
    def __init__(self):
        self.face_service = FaceRecognitionService()
        self.embedding_service = EmbeddingService(self.face_service)
        self.db = SessionLocal()
        logger.info("Face recognizer initialized")
    
    def recognize_face(self, face_image: np.ndarray) -> Optional[Tuple[int, float]]:
        """
        Recognize face in image
        
        Args:
            face_image: BGR face image (numpy array)
            
        Returns:
            (student_id, confidence) tuple or None
        """
        try:
            # Create embedding from face image
            embedding = self.face_service.create_embedding_from_array(face_image)
            
            if embedding is None:
                return None
            
            # Find matching student
            match = self.embedding_service.find_matching_student(self.db, embedding)
            
            return match
            
        except Exception as e:
            logger.error(f"Error recognizing face: {e}")
            return None
    
    def close(self):
        """Close database connection"""
        if self.db:
            self.db.close()

