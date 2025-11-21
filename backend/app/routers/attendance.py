"""
Attendance router
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta
from ..database import get_db
from ..models import AttendanceLog, Student, Camera
from pydantic import BaseModel

router = APIRouter()


class AttendanceResponse(BaseModel):
    id: int
    student_id: int | None
    camera_id: int | None
    detected_at: datetime
    confidence: float | None
    track_id: int | None
    image_path: str | None
    student: dict | None = None
    camera: dict | None = None
    
    class Config:
        from_attributes = True


class AttendanceStatsResponse(BaseModel):
    student_id: int
    student_name: str
    total_attendances: int
    last_attendance: datetime | None


@router.get("/", response_model=List[AttendanceResponse])
async def get_attendance(
    student_id: Optional[int] = None,
    camera_id: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get attendance logs"""
    query = db.query(AttendanceLog)
    
    if student_id:
        query = query.filter(AttendanceLog.student_id == student_id)
    if camera_id:
        query = query.filter(AttendanceLog.camera_id == camera_id)
    if date_from:
        try:
            date_from_dt = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
            query = query.filter(AttendanceLog.detected_at >= date_from_dt)
        except:
            pass
    if date_to:
        try:
            date_to_dt = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
            query = query.filter(AttendanceLog.detected_at <= date_to_dt)
        except:
            pass
    
    logs = query.order_by(desc(AttendanceLog.detected_at)).offset(skip).limit(limit).all()
    
    # Include student and camera info
    result = []
    for log in logs:
        log_dict = {
            "id": log.id,
            "student_id": log.student_id,
            "camera_id": log.camera_id,
            "detected_at": log.detected_at,
            "confidence": log.confidence,
            "track_id": log.track_id,
            "image_path": log.image_path,
            "student": None,
            "camera": None
        }
        
        if log.student:
            log_dict["student"] = {
                "id": log.student.id,
                "student_id": log.student.student_id,
                "full_name": log.student.full_name
            }
        
        if log.camera:
            log_dict["camera"] = {
                "id": log.camera.id,
                "name": log.camera.name,
                "location": log.camera.location
            }
        
        result.append(log_dict)
    
    return result


@router.get("/stats", response_model=List[AttendanceStatsResponse])
async def get_attendance_stats(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get attendance statistics by student"""
    query = db.query(
        AttendanceLog.student_id,
        func.count(AttendanceLog.id).label('total_attendances'),
        func.max(AttendanceLog.detected_at).label('last_attendance')
    ).filter(AttendanceLog.student_id.isnot(None))
    
    if date_from:
        try:
            date_from_dt = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
            query = query.filter(AttendanceLog.detected_at >= date_from_dt)
        except:
            pass
    if date_to:
        try:
            date_to_dt = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
            query = query.filter(AttendanceLog.detected_at <= date_to_dt)
        except:
            pass
    
    stats = query.group_by(AttendanceLog.student_id).all()
    
    result = []
    for stat in stats:
        student = db.query(Student).filter(Student.id == stat.student_id).first()
        result.append({
            "student_id": stat.student_id,
            "student_name": student.full_name if student else "Unknown",
            "total_attendances": stat.total_attendances,
            "last_attendance": stat.last_attendance
        })
    
    return result


@router.get("/latest", response_model=List[AttendanceResponse])
async def get_latest_attendance(
    limit: int = 10,
    since: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get latest attendance logs"""
    query = db.query(AttendanceLog).order_by(desc(AttendanceLog.detected_at))
    
    if since:
        try:
            since_dt = datetime.fromisoformat(since.replace('Z', '+00:00'))
            query = query.filter(AttendanceLog.detected_at > since_dt)
        except:
            pass
    
    logs = query.limit(limit).all()
    
    result = []
    for log in logs:
        log_dict = {
            "id": log.id,
            "student_id": log.student_id,
            "camera_id": log.camera_id,
            "detected_at": log.detected_at,
            "confidence": log.confidence,
            "track_id": log.track_id,
            "image_path": log.image_path,
            "student": None,
            "camera": None
        }
        
        if log.student:
            log_dict["student"] = {
                "id": log.student.id,
                "student_id": log.student.student_id,
                "full_name": log.student.full_name
            }
        
        if log.camera:
            log_dict["camera"] = {
                "id": log.camera.id,
                "name": log.camera.name,
                "location": log.camera.location
            }
        
        result.append(log_dict)
    
    return result


@router.get("/recent", response_model=List[AttendanceResponse])
async def get_recent_attendance(
    minutes: int = 5,
    db: Session = Depends(get_db)
):
    """Get attendance logs from the last N minutes"""
    since = datetime.utcnow() - timedelta(minutes=minutes)
    logs = db.query(AttendanceLog).filter(
        AttendanceLog.detected_at >= since
    ).order_by(desc(AttendanceLog.detected_at)).all()
    
    result = []
    for log in logs:
        log_dict = {
            "id": log.id,
            "student_id": log.student_id,
            "camera_id": log.camera_id,
            "detected_at": log.detected_at,
            "confidence": log.confidence,
            "track_id": log.track_id,
            "image_path": log.image_path,
            "student": None,
            "camera": None
        }
        
        if log.student:
            log_dict["student"] = {
                "id": log.student.id,
                "student_id": log.student.student_id,
                "full_name": log.student.full_name
            }
        
        if log.camera:
            log_dict["camera"] = {
                "id": log.camera.id,
                "name": log.camera.name,
                "location": log.camera.location
            }
        
        result.append(log_dict)
    
    return result


@router.post("/", response_model=AttendanceResponse)
async def create_attendance(
    student_id: int | None,
    camera_id: int | None,
    confidence: float | None = None,
    track_id: int | None = None,
    image_path: str | None = None,
    db: Session = Depends(get_db)
):
    """Create attendance log (called by video worker)"""
    attendance_log = AttendanceLog(
        student_id=student_id,
        camera_id=camera_id,
        confidence=confidence,
        track_id=track_id,
        image_path=image_path
    )
    
    db.add(attendance_log)
    db.commit()
    db.refresh(attendance_log)
    
    # Load student and camera info for broadcast
    student = None
    camera = None
    if attendance_log.student_id:
        student = db.query(Student).filter(Student.id == attendance_log.student_id).first()
    if attendance_log.camera_id:
        camera = db.query(Camera).filter(Camera.id == attendance_log.camera_id).first()
    
    # Broadcast to WebSocket clients (import here to avoid circular import)
    try:
        from ..routers.websocket import broadcast_attendance
        attendance_data = {
            "id": attendance_log.id,
            "student_id": attendance_log.student_id,
            "camera_id": attendance_log.camera_id,
            "detected_at": attendance_log.detected_at.isoformat(),
            "confidence": attendance_log.confidence,
            "track_id": attendance_log.track_id,
            "image_path": attendance_log.image_path,
            "student": {
                "id": student.id,
                "student_id": student.student_id,
                "full_name": student.full_name
            } if student else None,
            "camera": {
                "id": camera.id,
                "name": camera.name,
                "location": camera.location
            } if camera else None
        }
        await broadcast_attendance(attendance_data)
    except Exception as e:
        # WebSocket broadcast is optional, log error but don't fail
        import logging
        logging.getLogger(__name__).warning(f"Failed to broadcast attendance: {e}")
    
    return attendance_log

