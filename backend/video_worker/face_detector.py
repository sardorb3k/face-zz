"""
Face detector using SCRFD (via InsightFace)
"""
import cv2
import numpy as np
import logging
from typing import List, Tuple, Optional
from .config import FACE_DETECTION_THRESHOLD, USE_GPU
import os

logger = logging.getLogger(__name__)


class FaceDetector:
    """Face detection using SCRFD model"""
    
    def __init__(self):
        self.detector = None
        self._init_detector()
    
    def _init_detector(self):
        """Initialize face detector"""
        try:
            import insightface
            
            # Use InsightFace's SCRFD detector
            providers = ['CPUExecutionProvider']
            if USE_GPU:
                try:
                    import onnxruntime
                    if 'CUDAExecutionProvider' in onnxruntime.get_available_providers():
                        providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
                        logger.info("Face detector: Using GPU")
                except:
                    pass
            
            # Create FaceAnalysis app (includes detection)
            self.detector = insightface.app.FaceAnalysis(
                name="buffalo_l",  # Includes SCRFD detector
                providers=providers
            )
            self.detector.prepare(ctx_id=0, det_size=(640, 640))
            
            logger.info("Face detector initialized (SCRFD via InsightFace)")
            
        except ImportError:
            logger.error("InsightFace not installed. Please install: pip install insightface")
            raise
        except Exception as e:
            logger.error(f"Error initializing face detector: {e}")
            raise
    
    def detect_faces(self, image: np.ndarray) -> List[Tuple[int, int, int, int, float]]:
        """
        Detect faces in image
        
        Args:
            image: BGR image (numpy array)
            
        Returns:
            List of (x, y, w, h, confidence) tuples
        """
        if self.detector is None:
            return []
        
        try:
            faces = self.detector.get(image)
            
            if not faces:
                return []
            
            results = []
            for face in faces:
                bbox = face.bbox.astype(int)  # [x1, y1, x2, y2]
                confidence = face.det_score
                
                if confidence >= FACE_DETECTION_THRESHOLD:
                    x, y, w, h = bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1]
                    results.append((x, y, w, h, float(confidence)))
            
            return results
            
        except Exception as e:
            logger.error(f"Error detecting faces: {e}")
            return []
    
    def extract_face(self, image: np.ndarray, bbox: Tuple[int, int, int, int]) -> Optional[np.ndarray]:
        """
        Extract face region from image
        
        Args:
            image: BGR image
            bbox: (x, y, w, h) bounding box
            
        Returns:
            Extracted face image or None
        """
        x, y, w, h = bbox
        
        # Ensure coordinates are within image bounds
        h_img, w_img = image.shape[:2]
        x = max(0, x)
        y = max(0, y)
        w = min(w, w_img - x)
        h = min(h, h_img - y)
        
        if w <= 0 or h <= 0:
            return None
        
        face = image[y:y+h, x:x+w]
        return face

