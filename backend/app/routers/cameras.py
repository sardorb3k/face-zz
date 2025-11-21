"""
Cameras router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Camera
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


class CameraCreate(BaseModel):
    name: str
    rtsp_url: str | None = None
    camera_type: str  # 'rtsp' or 'laptop'
    camera_index: int | None = None
    location: str | None = None
    is_active: bool = True


class CameraResponse(BaseModel):
    id: int
    name: str
    rtsp_url: str | None
    camera_type: str
    camera_index: int | None
    is_active: bool
    location: str | None
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[CameraResponse])
async def get_cameras(
    is_active: bool | None = None,
    db: Session = Depends(get_db)
):
    """Get all cameras"""
    query = db.query(Camera)
    
    if is_active is not None:
        query = query.filter(Camera.is_active == is_active)
    
    cameras = query.all()
    return cameras


@router.get("/{camera_id}", response_model=CameraResponse)
async def get_camera(camera_id: int, db: Session = Depends(get_db)):
    """Get camera by ID"""
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera


@router.post("/", response_model=CameraResponse)
async def create_camera(camera: CameraCreate, db: Session = Depends(get_db)):
    """Create a new camera"""
    if camera.camera_type not in ['rtsp', 'laptop']:
        raise HTTPException(status_code=400, detail="camera_type must be 'rtsp' or 'laptop'")
    
    if camera.camera_type == 'rtsp' and not camera.rtsp_url:
        raise HTTPException(status_code=400, detail="rtsp_url is required for RTSP cameras")
    
    if camera.camera_type == 'laptop' and camera.camera_index is None:
        raise HTTPException(status_code=400, detail="camera_index is required for laptop cameras")
    
    db_camera = Camera(**camera.dict())
    db.add(db_camera)
    db.commit()
    db.refresh(db_camera)
    return db_camera


@router.put("/{camera_id}", response_model=CameraResponse)
async def update_camera(
    camera_id: int,
    camera: CameraCreate,
    db: Session = Depends(get_db)
):
    """Update camera"""
    db_camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not db_camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    if camera.camera_type not in ['rtsp', 'laptop']:
        raise HTTPException(status_code=400, detail="camera_type must be 'rtsp' or 'laptop'")
    
    for key, value in camera.dict().items():
        setattr(db_camera, key, value)
    
    db.commit()
    db.refresh(db_camera)
    return db_camera


@router.delete("/{camera_id}")
async def delete_camera(camera_id: int, db: Session = Depends(get_db)):
    """Delete camera"""
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    db.delete(camera)
    db.commit()
    return {"message": "Camera deleted successfully"}

