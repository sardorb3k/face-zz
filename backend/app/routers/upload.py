"""
Upload router for face images
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Student, StudentImage, StudentEmbedding
from ..services.face_recognition import FaceRecognitionService
from ..services.embedding_service import EmbeddingService
from ..config import IMAGES_DIR, FACE_RECOGNITION_THRESHOLD
from pathlib import Path
import shutil
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services (singleton pattern)
_face_recognition_service = None
_embedding_service = None


def get_face_recognition_service() -> FaceRecognitionService:
    """Get or create face recognition service"""
    global _face_recognition_service
    if _face_recognition_service is None:
        _face_recognition_service = FaceRecognitionService()
    return _face_recognition_service


def get_embedding_service() -> EmbeddingService:
    """Get or create embedding service"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService(get_face_recognition_service())
    return _embedding_service


@router.post("/face")
async def upload_face(
    student_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload face image for a student"""
    # Check if student exists
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Check if student already has 5 images
    existing_images = db.query(StudentImage).filter(StudentImage.student_id == student_id).count()
    if existing_images >= 5:
        raise HTTPException(status_code=400, detail="Maximum 5 images per student allowed")
    
    # Save file
    file_extension = Path(file.filename).suffix
    file_name = f"{student_id}_{uuid.uuid4()}{file_extension}"
    file_path = IMAGES_DIR / file_name
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        raise HTTPException(status_code=500, detail="Error saving file")
    
    # Create embedding
    face_service = get_face_recognition_service()
    
    # Try to create embedding
    embedding = None
    error_message = None
    
    try:
        embedding = face_service.create_embedding(str(file_path))
    except Exception as e:
        logger.error(f"Error creating embedding: {e}")
        error_message = str(e)
    
    if embedding is None:
        # Try to get more details about why face detection failed
        import cv2
        test_image = cv2.imread(str(file_path))
        if test_image is None:
            file_path.unlink(missing_ok=True)
            raise HTTPException(status_code=400, detail="Could not read image file")
        
        # Try InsightFace directly
        try:
            import insightface
            app = insightface.app.FaceAnalysis(name="buffalo_l", providers=['CPUExecutionProvider'])
            app.prepare(ctx_id=0, det_size=(640, 640))
            faces = app.get(test_image)
            
            if not faces or len(faces) == 0:
                file_path.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=400, 
                    detail="Could not detect face in image. Please ensure the image contains a clear face."
                )
            else:
                # Face detected but embedding creation failed - try again with better error handling
                logger.warning(f"Face detected but embedding creation failed. Retrying...")
                # Try once more
                embedding = face_service.create_embedding(str(file_path))
                if embedding is None:
                    file_path.unlink(missing_ok=True)
                    raise HTTPException(
                        status_code=400,
                        detail=f"Face detected but could not create embedding. Error: {error_message or 'Unknown error'}"
                    )
        except ImportError:
            # InsightFace not available, use generic error
            file_path.unlink(missing_ok=True)
            raise HTTPException(
                status_code=400,
                detail="Could not detect face in image. Please ensure the image contains a clear, front-facing face."
            )
        except Exception as e:
            file_path.unlink(missing_ok=True)
            raise HTTPException(
                status_code=400,
                detail=f"Error processing image: {str(e)}"
            )
    
    # Save image record
    student_image = StudentImage(
        student_id=student_id,
        image_path=str(file_path)
    )
    db.add(student_image)
    db.commit()
    
    # Update student embedding (average all images)
    embedding_service = get_embedding_service()
    embedding_created = embedding_service.update_student_embedding(db, student_id)
    
    return {
        "success": True,
        "message": "Face image uploaded successfully",
        "student_id": student_id,
        "embedding_created": embedding_created,
        "image_path": str(file_path)
    }


@router.post("/face/test")
async def test_face(
    student_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Test face recognition against a student"""
    # Check if student exists
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Save temporary file
    file_extension = Path(file.filename).suffix
    temp_file = IMAGES_DIR / f"temp_{uuid.uuid4()}{file_extension}"
    
    try:
        with open(temp_file, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Create embedding from uploaded image
        face_service = get_face_recognition_service()
        query_embedding = face_service.create_embedding(str(temp_file))
        
        if query_embedding is None:
            raise HTTPException(status_code=400, detail="Could not detect face in image")
        
        # Find matching student
        embedding_service = get_embedding_service()
        match = embedding_service.find_matching_student(db, query_embedding, FACE_RECOGNITION_THRESHOLD)
        
        if match and match[0] == student_id:
            return {
                "success": True,
                "message": "Face matches student",
                "confidence": match[1]
            }
        else:
            return {
                "success": False,
                "message": "Face does not match student",
                "confidence": match[1] if match else 0.0
            }
    finally:
        # Clean up temp file
        temp_file.unlink(missing_ok=True)

