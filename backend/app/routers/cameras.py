"""
Cameras router
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Camera
from pydantic import BaseModel
from datetime import datetime
import cv2
import threading
import time
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Store active camera streams
_active_streams = {}
_stream_locks = {}


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
    
    # Stop stream if active
    if camera_id in _active_streams:
        _active_streams[camera_id].release()
        del _active_streams[camera_id]
        if camera_id in _stream_locks:
            del _stream_locks[camera_id]
    
    db.delete(camera)
    db.commit()
    return {"message": "Camera deleted successfully"}


def generate_mjpeg_stream(camera_id: int, camera: Camera):
    """Generate MJPEG stream from camera"""
    cap = None
    consecutive_failures = 0
    max_failures = 10
    reconnect_delay = 1.0
    
    try:
        while True:
            # Open camera
            if camera.camera_type == "rtsp" and camera.rtsp_url:
                logger.info(f"Opening RTSP stream: {camera.rtsp_url}")
                cap = cv2.VideoCapture(camera.rtsp_url, cv2.CAP_FFMPEG)
                # Set buffer size to reduce latency
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            elif camera.camera_type == "laptop" and camera.camera_index is not None:
                logger.info(f"Opening laptop camera: index {camera.camera_index}")
                cap = cv2.VideoCapture(camera.camera_index)
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            else:
                logger.error(f"Invalid camera configuration: {camera.camera_type}")
                return
            
            if not cap.isOpened():
                logger.error(f"Failed to open camera {camera_id}")
                consecutive_failures += 1
                if consecutive_failures >= max_failures:
                    logger.error(f"Too many failures for camera {camera_id}, giving up")
                    return
                time.sleep(reconnect_delay)
                continue
            
            # Set frame size (optional, for performance)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            # Set FPS
            cap.set(cv2.CAP_PROP_FPS, 30)
            
            logger.info(f"Stream started for camera {camera_id}")
            consecutive_failures = 0  # Reset failure count on successful connection
            
            frame_count = 0
            frame_read_failures = 0
            max_frame_failures = 5
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    frame_read_failures += 1
                    if frame_read_failures >= max_frame_failures:
                        logger.warning(f"Too many frame read failures for camera {camera_id}, reconnecting...")
                        break  # Break inner loop to reconnect
                    
                    logger.warning(f"Failed to read frame from camera {camera_id} (attempt {frame_read_failures}/{max_frame_failures})")
                    time.sleep(0.1)
                    continue
                
                # Reset frame read failures on success
                frame_read_failures = 0
                
                # Skip frames to reduce latency (read but don't process old frames)
                # Only skip if we have a good connection
                try:
                    for _ in range(2):
                        cap.grab()
                except:
                    pass  # Ignore grab errors
                
                # Encode frame as JPEG
                ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                if not ret:
                    continue
                
                # Yield MJPEG frame
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                
                frame_count += 1
                if frame_count % 30 == 0:
                    logger.debug(f"Streaming frame {frame_count} for camera {camera_id}")
                
                # Small delay to control frame rate
                time.sleep(0.033)  # ~30 FPS
            
            # If we get here, connection was lost - try to reconnect
            if cap is not None:
                cap.release()
                cap = None
            logger.warning(f"Connection lost for camera {camera_id}, attempting to reconnect...")
            time.sleep(reconnect_delay)
            
    except Exception as e:
        logger.error(f"Error in stream for camera {camera_id}: {e}", exc_info=True)
    finally:
        if cap is not None:
            cap.release()
            logger.info(f"Stream closed for camera {camera_id}")
        if camera_id in _active_streams:
            del _active_streams[camera_id]
        if camera_id in _stream_locks:
            del _stream_locks[camera_id]


@router.get("/{camera_id}/stream")
async def get_camera_stream(camera_id: int, db: Session = Depends(get_db)):
    """Get MJPEG stream from camera"""
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    if not camera.is_active:
        raise HTTPException(status_code=400, detail="Camera is not active")
    
    # Check if camera has valid source
    if camera.camera_type == "rtsp" and not camera.rtsp_url:
        raise HTTPException(status_code=400, detail="RTSP URL not configured")
    if camera.camera_type == "laptop" and camera.camera_index is None:
        raise HTTPException(status_code=400, detail="Camera index not configured")
    
    return StreamingResponse(
        generate_mjpeg_stream(camera_id, camera),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@router.get("/stream/rtsp")
async def get_rtsp_stream(rtsp_url: str):
    """Get MJPEG stream from RTSP URL (for config cameras without DB ID)"""
    if not rtsp_url:
        raise HTTPException(status_code=400, detail="RTSP URL is required")
    
    # Create a temporary camera object for streaming
    from types import SimpleNamespace
    temp_camera = SimpleNamespace()
    temp_camera.camera_type = "rtsp"
    temp_camera.rtsp_url = rtsp_url
    temp_camera.camera_index = None
    
    return StreamingResponse(
        generate_mjpeg_stream(0, temp_camera),  # Use 0 as temp ID
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

