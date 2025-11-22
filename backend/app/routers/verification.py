"""
Face verification router
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import FaceVerification, Student, User, StudentImage
from ..routers.auth import get_current_user, get_current_admin
from ..services.face_recognition import FaceRecognitionService
from ..services.embedding_service import EmbeddingService
from ..config import IMAGES_DIR, FACE_RECOGNITION_THRESHOLD
from pathlib import Path
from datetime import datetime
import shutil
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
_face_recognition_service = None
_embedding_service = None


def get_face_recognition_service() -> FaceRecognitionService:
    global _face_recognition_service
    if _face_recognition_service is None:
        _face_recognition_service = FaceRecognitionService()
    return _face_recognition_service


def get_embedding_service() -> EmbeddingService:
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService(get_face_recognition_service())
    return _embedding_service


@router.post("/verify")
async def verify_face(
    file: UploadFile = File(...),
    camera_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Verify face for student (student can upload their face)"""
    if current_user.role != "student" or not current_user.student_id:
        raise HTTPException(status_code=403, detail="Only students can verify their face")
    
    student_id = current_user.student_id
    
    # Get or create default camera for student verification
    from ..models import Camera
    if camera_id:
        camera = db.query(Camera).filter(Camera.id == camera_id).first()
        if not camera:
            raise HTTPException(status_code=404, detail="Camera not found")
    else:
        # Use default laptop camera if no camera_id provided
        camera = db.query(Camera).filter(
            Camera.camera_type == "laptop",
            Camera.is_active == True
        ).first()
        
        # If no laptop camera exists, create one
        if not camera:
            camera = Camera(
                name="Laptop Camera",
                camera_type="laptop",
                camera_index=0,
                is_active=True,
                location="Student Verification"
            )
            db.add(camera)
            db.commit()
            db.refresh(camera)
    
    # Save file
    file_extension = Path(file.filename).suffix
    file_name = f"verify_{student_id}_{uuid.uuid4()}{file_extension}"
    file_path = IMAGES_DIR / file_name
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        raise HTTPException(status_code=500, detail="Error saving file")
    
    # Create embedding
    face_service = get_face_recognition_service()
    embedding = face_service.create_embedding(str(file_path))
    
    if embedding is None:
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="Could not detect face in image")
    
    # Get student's embedding from database
    from ..models import StudentEmbedding, StudentImage
    student_embedding_record = db.query(StudentEmbedding).filter(
        StudentEmbedding.student_id == student_id
    ).first()
    
    confidence = None
    is_match = False
    image_uploaded = False
    
    if student_embedding_record:
        # Compare with student's own embedding
        student_embedding = student_embedding_record.get_embedding_array()
        match, similarity = face_service.compare_faces(
            embedding,
            student_embedding,
            FACE_RECOGNITION_THRESHOLD
        )
        confidence = float(similarity)
        is_match = match
    else:
        # Student has no embedding yet - automatically upload this face image
        # Check if student already has 5 images
        existing_images = db.query(StudentImage).filter(StudentImage.student_id == student_id).count()
        
        if existing_images < 5:
            # Move file from verify_ to student_images directory
            file_extension = Path(file_path).suffix
            new_file_name = f"{student_id}_{uuid.uuid4()}{file_extension}"
            new_file_path = IMAGES_DIR / new_file_name
            
            try:
                shutil.move(str(file_path), str(new_file_path))
                
                # Create student image record
                student_image = StudentImage(
                    student_id=student_id,
                    image_path=str(new_file_path)
                )
                db.add(student_image)
                db.commit()
                
                # Update student embedding
                embedding_service = get_embedding_service()
                embedding_created = embedding_service.update_student_embedding(db, student_id)
                
                image_uploaded = True
                file_path = new_file_path  # Update file_path for verification record
                
                logger.info(f"Automatically uploaded face image for student {student_id} and created embedding")
            except Exception as e:
                logger.error(f"Error uploading face image: {e}")
                # Keep original file_path for verification
        else:
            logger.warning(f"Student {student_id} already has 5 images, cannot upload more")
    
    # Create verification request
    verification = FaceVerification(
        student_id=student_id,
        camera_id=camera.id if camera else None,
        image_path=str(file_path),
        verification_status="pending" if not is_match else "approved",  # Auto-approve if match
        confidence=confidence if confidence is not None else 0.0  # Database requires float, but we'll return None in API
    )
    db.add(verification)
    
    # If match, mark as reviewed
    if is_match:
        verification.verification_status = "approved"
        verification.reviewed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(verification)
    
    # Prepare response message
    if image_uploaded:
        message = "Yuz rasmi muvaffaqiyatli yuklandi va embedding yaratildi! Endi davomat olishingiz mumkin."
    elif is_match:
        message = "Face verified successfully"
    elif student_embedding_record:
        message = "Face does not match student"
    else:
        message = "Yuz rasmi yuklandi, lekin sizda allaqachon 5 ta rasm bor. Admin tomonidan ko'rib chiqilmoqda."
    
    return {
        "success": True,
        "verification_id": verification.id,
        "is_match": is_match,
        "confidence": confidence,  # None if no embedding, otherwise similarity score
        "image_uploaded": image_uploaded,
        "message": message
    }


@router.get("/pending")
async def get_pending_verifications(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Get pending face verifications (admin only)"""
    from ..models import Camera
    
    verifications = db.query(FaceVerification).filter(
        FaceVerification.verification_status == "pending"
    ).all()
    
    result = []
    for v in verifications:
        camera_info = None
        if v.camera_id:
            camera = db.query(Camera).filter(Camera.id == v.camera_id).first()
            if camera:
                camera_info = {
                    "id": camera.id,
                    "name": camera.name,
                    "location": camera.location,
                    "camera_type": camera.camera_type
                }
        
        result.append({
            "id": v.id,
            "student_id": v.student_id,
            "student_name": v.student.full_name if v.student else "Unknown",
            "image_path": v.image_path,
            "confidence": v.confidence,
            "camera": camera_info,
            "created_at": v.created_at.isoformat() if v.created_at else None
        })
    
    return result


@router.post("/{verification_id}/approve")
async def approve_verification(
    verification_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Approve face verification (admin only)"""
    verification = db.query(FaceVerification).filter(
        FaceVerification.id == verification_id
    ).first()
    
    if not verification:
        raise HTTPException(status_code=404, detail="Verification not found")
    
    if verification.verification_status != "pending":
        raise HTTPException(status_code=400, detail="Verification already processed")
    
    # Move image to student_images
    old_path = Path(verification.image_path)
    if old_path.exists():
        # Check if student already has 5 images
        existing_count = db.query(StudentImage).filter(
            StudentImage.student_id == verification.student_id
        ).count()
        
        if existing_count < 5:
            new_name = f"{verification.student_id}_{uuid.uuid4()}{old_path.suffix}"
            new_path = IMAGES_DIR / new_name
            shutil.move(str(old_path), str(new_path))
            
            # Create student image record
            student_image = StudentImage(
                student_id=verification.student_id,
                image_path=str(new_path)
            )
            db.add(student_image)
            
            # Update student embedding
            embedding_service = get_embedding_service()
            embedding_service.update_student_embedding(db, verification.student_id)
        else:
            # Delete if student already has 5 images
            old_path.unlink(missing_ok=True)
    
    # Update verification
    verification.verification_status = "approved"
    verification.reviewed_by = current_admin.id
    verification.reviewed_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Verification approved", "verification_id": verification_id}


@router.post("/{verification_id}/reject")
async def reject_verification(
    verification_id: int,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Reject face verification (admin only)"""
    verification = db.query(FaceVerification).filter(
        FaceVerification.id == verification_id
    ).first()
    
    if not verification:
        raise HTTPException(status_code=404, detail="Verification not found")
    
    if verification.verification_status != "pending":
        raise HTTPException(status_code=400, detail="Verification already processed")
    
    # Delete image
    image_path = Path(verification.image_path)
    if image_path.exists():
        image_path.unlink(missing_ok=True)
    
    # Update verification
    verification.verification_status = "rejected"
    verification.reviewed_by = current_admin.id
    verification.reviewed_at = datetime.utcnow()
    verification.notes = notes
    
    db.commit()
    
    return {"message": "Verification rejected", "verification_id": verification_id}

