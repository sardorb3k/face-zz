"""
Video worker main entry point
"""
import cv2
import logging
import time
import sys
from pathlib import Path
from typing import Dict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from .camera_manager import CameraManager
from .face_detector import FaceDetector
from .face_recognizer import FaceRecognizer
from .tracker import Tracker
from .attendance_manager import AttendanceManager
from .config import FRAME_SKIP
from app.database import SessionLocal
from app.models import Camera

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VideoWorker:
    """Main video processing worker"""
    
    def __init__(self):
        self.camera_managers: list[CameraManager] = []
        self.face_detector = FaceDetector()
        self.face_recognizer = FaceRecognizer()
        self.trackers: Dict[int, Tracker] = {}  # Per-camera trackers
        self.attendance_manager = AttendanceManager()
        self.frame_counters: Dict[int, int] = {}  # Per-camera frame counters
        self.running = False
    
    def initialize_cameras(self):
        """Initialize cameras from database (only active RTSP cameras)"""
        from app.config import USE_LAPTOP_CAMERA, LAPTOP_CAMERA_INDEX
        
        db = SessionLocal()
        try:
            # Get active RTSP cameras from database
            cameras = db.query(Camera).filter(
                Camera.is_active == True,
                Camera.camera_type == "rtsp"
            ).all()
            
            # Create camera managers for RTSP cameras
            for camera in cameras:
                if not camera.rtsp_url:
                    logger.warning(f"Camera {camera.id}: RTSP URL not set, skipping")
                    continue
                    
                manager = CameraManager(
                    camera_id=camera.id,
                    camera_type=camera.camera_type,
                    rtsp_url=camera.rtsp_url,
                    camera_index=camera.camera_index
                )
                self.camera_managers.append(manager)
                self.trackers[camera.id] = Tracker()
                self.frame_counters[camera.id] = 0
                logger.info(f"Added RTSP camera {camera.id}: {camera.rtsp_url}")
            
            # Add laptop camera only if enabled in env
            if USE_LAPTOP_CAMERA and LAPTOP_CAMERA_INDEX is not None:
                # Check if laptop camera already exists in database
                laptop_camera = db.query(Camera).filter(
                    Camera.camera_type == "laptop",
                    Camera.is_active == True
                ).first()
                
                if laptop_camera:
                    # Use database laptop camera
                    manager = CameraManager(
                        camera_id=laptop_camera.id,
                        camera_type=laptop_camera.camera_type,
                        rtsp_url=laptop_camera.rtsp_url,
                        camera_index=laptop_camera.camera_index or LAPTOP_CAMERA_INDEX
                    )
                    logger.info(f"Added laptop camera from database: {laptop_camera.id}")
                else:
                    # Create temporary laptop camera manager (not in database)
                    laptop_id = max([c.id for c in cameras] + [0]) + 1 if cameras else 1
                    manager = CameraManager(
                        camera_id=laptop_id,
                        camera_type="laptop",
                        rtsp_url=None,
                        camera_index=LAPTOP_CAMERA_INDEX
                    )
                    logger.info(f"Added laptop camera from config: index {LAPTOP_CAMERA_INDEX}")
                
                self.camera_managers.append(manager)
                self.trackers[manager.camera_id] = Tracker()
                self.frame_counters[manager.camera_id] = 0
            
            logger.info(f"Initialized {len(self.camera_managers)} cameras ({len(cameras)} RTSP, {'1 laptop' if USE_LAPTOP_CAMERA else '0 laptop'})")
            
        finally:
            db.close()
    
    def connect_cameras(self):
        """Connect to all cameras"""
        for manager in self.camera_managers:
            if not manager.connect():
                logger.warning(f"Failed to connect camera {manager.camera_id}, will retry...")
    
    def process_frame(self, camera_id: int, frame):
        """Process a single frame"""
        # Skip frames for performance
        self.frame_counters[camera_id] += 1
        if self.frame_counters[camera_id] % FRAME_SKIP != 0:
            return
        
        try:
            # Detect faces
            detections = self.face_detector.detect_faces(frame)
            
            if detections:
                logger.debug(f"📸 {len(detections)} ta yuz aniqlandi (camera: {camera_id})")
            
            if not detections:
                return
            
            # Track faces
            tracker = self.trackers.get(camera_id)
            if tracker:
                tracked = tracker.update(detections, frame)
            else:
                tracked = [(x, y, w, h, idx, conf) for idx, (x, y, w, h, conf) in enumerate(detections)]
            
            # Recognize and log attendance
            for x, y, w, h, track_id, conf in tracked:
                # Extract face
                face_image = self.face_detector.extract_face(frame, (x, y, w, h))
                
                if face_image is None:
                    continue
                
                # Recognize face
                recognition_result = self.face_recognizer.recognize_face(face_image)
                
                if recognition_result:
                    student_id, similarity = recognition_result
                    
                    # Log recognition
                    logger.info(f"🎓 Talaba aniqlandi: Student ID {student_id} (confidence: {similarity:.3f}, track: {track_id}, camera: {camera_id})")
                    
                    # Log attendance
                    success = self.attendance_manager.log_attendance(
                        student_id=student_id,
                        camera_id=camera_id,
                        confidence=similarity,
                        track_id=track_id,
                        face_image=face_image
                    )
                    
                    if not success:
                        logger.debug(f"⚠️  Duplicate prevention: Student {student_id} on camera {camera_id} - attendance not logged")
                else:
                    # Log when face detected but not recognized
                    logger.debug(f"❓ Yuz aniqlandi, lekin talaba tanilmadi (track: {track_id}, camera: {camera_id})")
        
        except Exception as e:
            logger.error(f"Error processing frame from camera {camera_id}: {e}")
    
    def run(self):
        """Main processing loop"""
        logger.info("Starting video worker...")
        
        self.initialize_cameras()
        self.connect_cameras()
        
        self.running = True
        
        # Check if there are any cameras
        if not self.camera_managers:
            logger.warning("Hech qanday kamera topilmadi, video worker to'xtatilmoqda")
            return
        
        while self.running:
            try:
                # Process each camera
                for manager in self.camera_managers:
                    if not manager.is_connected:
                        # Try to reconnect
                        if not manager.reconnect():
                            continue
                    
                    # Read frame
                    result = manager.read_frame()
                    
                    if result is None:
                        # Frame read failed, will retry on next iteration
                        continue
                    
                    success, frame = result
                    
                    if success and frame is not None:
                        self.process_frame(manager.camera_id, frame)
                
                # Cleanup old attendance records periodically
                self.attendance_manager.cleanup_old_records()
                
                # Small delay to prevent CPU overload
                time.sleep(0.01)
                
            except KeyboardInterrupt:
                logger.info("Received interrupt signal, shutting down...")
                self.running = False
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(1)
        
        self.shutdown()
    
    def shutdown(self):
        """Cleanup and shutdown"""
        logger.info("Shutting down video worker...")
        
        for manager in self.camera_managers:
            manager.disconnect()
        
        self.face_recognizer.close()
        
        logger.info("Video worker stopped")


def main():
    """Entry point"""
    worker = VideoWorker()
    try:
        worker.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

