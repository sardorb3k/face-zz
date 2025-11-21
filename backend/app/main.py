"""
FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import init_db, engine
from .models import Base
from .config import CORS_ORIGINS
from .routers import students, attendance, upload, cameras, websocket
from .static_files import setup_static_files
from .background_tasks import start_video_worker, stop_video_worker, is_video_worker_running
from .config import USE_LAPTOP_CAMERA, RTSP_CAMERAS, LAPTOP_CAMERA_INDEX
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
init_db()
logger.info("Database initialized")

# Create FastAPI app
app = FastAPI(
    title="Face Recognition Attendance System",
    description="Real-time face recognition attendance system",
    version="1.0.0"
)

# Setup static files
setup_static_files(app)
logger.info("Static files configured")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(students.router, prefix="/api/students", tags=["students"])
app.include_router(attendance.router, prefix="/api/attendance", tags=["attendance"])
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
app.include_router(cameras.router, prefix="/api/cameras", tags=["cameras"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])


@app.get("/")
async def root():
    return {"message": "Face Recognition Attendance System API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.on_event("startup")
async def startup_event():
    """Start video worker on startup"""
    # Check if video worker should start automatically
    auto_start = os.getenv("AUTO_START_VIDEO_WORKER", "true").lower() == "true"
    
    if auto_start:
        # Check if there are cameras configured
        has_cameras = (USE_LAPTOP_CAMERA and LAPTOP_CAMERA_INDEX is not None) or len(RTSP_CAMERAS) > 0
        
        if has_cameras:
            logger.info("Video worker avtomatik ishga tushirilmoqda...")
            start_video_worker()
        else:
            logger.info("Kamera sozlanganmagan, video worker ishga tushirilmaydi")
    else:
        logger.info("AUTO_START_VIDEO_WORKER=false, video worker qo'lda ishga tushirilishi kerak")


@app.on_event("shutdown")
async def shutdown_event():
    """Stop video worker on shutdown"""
    if is_video_worker_running():
        logger.info("Video worker to'xtatilmoqda...")
        stop_video_worker()


@app.post("/api/video-worker/start")
async def start_video_worker_endpoint():
    """Manually start video worker"""
    if is_video_worker_running():
        return {"status": "already_running", "message": "Video worker allaqachon ishlayapti"}
    
    start_video_worker()
    return {"status": "started", "message": "Video worker ishga tushirildi"}


@app.post("/api/video-worker/stop")
async def stop_video_worker_endpoint():
    """Manually stop video worker"""
    if not is_video_worker_running():
        return {"status": "not_running", "message": "Video worker ishlamayapti"}
    
    stop_video_worker()
    return {"status": "stopped", "message": "Video worker to'xtatish so'rovi yuborildi"}


@app.get("/api/video-worker/status")
async def video_worker_status():
    """Get video worker status"""
    return {
        "running": is_video_worker_running(),
        "auto_start": os.getenv("AUTO_START_VIDEO_WORKER", "true").lower() == "true"
    }

