"""
Embedding service for efficient student face recognition
"""
import numpy as np
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from ..models import Student, StudentImage, StudentEmbedding
from .face_recognition import FaceRecognitionService
from ..config import FACE_RECOGNITION_THRESHOLD
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for managing and searching student embeddings"""
    
    def __init__(self, face_recognition_service: FaceRecognitionService):
        self.face_recognition_service = face_recognition_service
        self._embeddings_cache: Optional[List[Tuple[int, np.ndarray]]] = None
        self._cache_valid = False
    
    def invalidate_cache(self):
        """Invalidate the embeddings cache"""
        self._cache_valid = False
        self._embeddings_cache = None
    
    def load_all_embeddings(self, db: Session) -> List[Tuple[int, np.ndarray]]:
        """
        Load all student embeddings from database
        
        Returns:
            List of (student_id, embedding_array) tuples
        """
        if self._cache_valid and self._embeddings_cache is not None:
            return self._embeddings_cache
        
        embeddings = []
        student_embeddings = db.query(StudentEmbedding).all()
        
        for se in student_embeddings:
            try:
                embedding_array = se.get_embedding_array()
                if embedding_array is not None and len(embedding_array) > 0:
                    embeddings.append((se.student_id, embedding_array))
            except Exception as e:
                logger.error(f"Error loading embedding for student {se.student_id}: {e}")
                continue
        
        self._embeddings_cache = embeddings
        self._cache_valid = True
        
        logger.info(f"Loaded {len(embeddings)} student embeddings")
        return embeddings
    
    def compute_average_embedding(self, embeddings: List[np.ndarray]) -> np.ndarray:
        """
        Compute average of multiple embeddings and L2 normalize
        
        Args:
            embeddings: List of embedding arrays
            
        Returns:
            Averaged and normalized embedding
        """
        if not embeddings:
            raise ValueError("Cannot compute average of empty embeddings list")
        
        if len(embeddings) == 1:
            return embeddings[0]
        
        # Average all embeddings
        avg_embedding = np.mean(embeddings, axis=0)
        
        # L2 normalize
        norm = np.linalg.norm(avg_embedding)
        if norm > 0:
            avg_embedding = avg_embedding / norm
        
        return avg_embedding.astype(np.float32)
    
    def update_student_embedding(self, db: Session, student_id: int) -> bool:
        """
        Update student embedding by averaging all their image embeddings
        
        Args:
            db: Database session
            student_id: Student ID
            
        Returns:
            True if embedding was created/updated, False otherwise
        """
        # Get all images for this student
        images = db.query(StudentImage).filter(StudentImage.student_id == student_id).all()
        
        if not images:
            logger.warning(f"No images found for student {student_id}")
            # Delete existing embedding if no images
            db.query(StudentEmbedding).filter(StudentEmbedding.student_id == student_id).delete()
            db.commit()
            self.invalidate_cache()
            return False
        
        # Create embeddings from all images
        image_embeddings = []
        for image in images:
            try:
                embedding = self.face_recognition_service.create_embedding(image.image_path)
                if embedding is not None:
                    image_embeddings.append(embedding)
            except Exception as e:
                logger.error(f"Error creating embedding from {image.image_path}: {e}")
                continue
        
        if not image_embeddings:
            logger.warning(f"Could not create embeddings from images for student {student_id}")
            # Delete existing embedding if no valid embeddings
            db.query(StudentEmbedding).filter(StudentEmbedding.student_id == student_id).delete()
            db.commit()
            self.invalidate_cache()
            return False
        
        # Compute average embedding
        avg_embedding = self.compute_average_embedding(image_embeddings)
        
        # Update or create embedding in database
        existing = db.query(StudentEmbedding).filter(StudentEmbedding.student_id == student_id).first()
        
        if existing:
            existing.set_embedding_array(avg_embedding)
        else:
            new_embedding = StudentEmbedding(
                student_id=student_id,
                embedding=avg_embedding.astype(np.float32).tobytes()
            )
            db.add(new_embedding)
        
        db.commit()
        self.invalidate_cache()
        
        logger.info(f"Updated embedding for student {student_id} from {len(image_embeddings)} images")
        return True
    
    def find_matching_student(
        self,
        db: Session,
        query_embedding: np.ndarray,
        threshold: Optional[float] = None
    ) -> Optional[Tuple[int, float]]:
        """
        Find matching student for a given embedding
        
        Args:
            db: Database session
            query_embedding: Embedding to search for
            threshold: Similarity threshold (default from config)
            
        Returns:
            (student_id, similarity_score) tuple or None
        """
        if threshold is None:
            threshold = FACE_RECOGNITION_THRESHOLD
        
        # Load all embeddings
        student_embeddings = self.load_all_embeddings(db)
        
        if not student_embeddings:
            return None
        
        # Find best match
        best_match = None
        best_similarity = threshold
        
        for student_id, student_embedding in student_embeddings:
            match, similarity = self.face_recognition_service.compare_faces(
                query_embedding,
                student_embedding,
                threshold
            )
            
            if match and similarity > best_similarity:
                best_similarity = similarity
                best_match = (student_id, similarity)
        
        return best_match

