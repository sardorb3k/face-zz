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
        
        # Pre-load embeddings on initialization
        embeddings = self.embedding_service.load_all_embeddings(self.db)
        logger.info(f"Face recognizer initialized with {len(embeddings)} student embeddings")
        print(f"✅ Face recognizer: {len(embeddings)} ta student embedding yuklandi")
        
        if len(embeddings) == 0:
            logger.warning("⚠️  Hech qanday student embedding topilmadi! Davomat olish uchun talabalarga yuz rasmlari yuklanishi kerak.")
            print("⚠️  MUAMMO: Hech qanday student embedding topilmadi!")
            print("   Talabalarga yuz rasmlari yuklanishi kerak.")
        else:
            logger.info(f"✅ {len(embeddings)} ta student embedding yuklandi va ishlatilmoqda")
            print(f"✅ {len(embeddings)} ta embedding yuklandi - video worker bu embedding'lar asosida yuzlarni izlaydi")
            
            # Show which students have embeddings
            from app.models import Student
            for student_id, _ in embeddings:
                student = self.db.query(Student).filter(Student.id == student_id).first()
                if student:
                    print(f"   - {student.full_name} (ID: {student_id})")
    
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
                logger.debug("Embedding yaratib bo'lmadi")
                return None
            
            # Find matching student
            match = self.embedding_service.find_matching_student(self.db, embedding)
            
            if match:
                logger.debug(f"Match topildi: Student ID {match[0]}, confidence: {match[1]:.3f}")
            else:
                logger.debug("Match topilmadi (embedding yo'q yoki confidence past)")
            
            return match
            
        except Exception as e:
            logger.error(f"Error recognizing face: {e}", exc_info=True)
            return None
    
    def close(self):
        """Close database connection"""
        if self.db:
            self.db.close()

