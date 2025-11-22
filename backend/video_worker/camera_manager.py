"""
Camera manager for RTSP and laptop cameras
"""
import cv2
import logging
from typing import Optional, Tuple
from .config import RTSP_CAMERAS, LAPTOP_CAMERA_INDEX, USE_LAPTOP_CAMERA, RECONNECT_DELAY, MAX_RECONNECT_ATTEMPTS
import time

logger = logging.getLogger(__name__)


class CameraManager:
    """Manages camera connections (RTSP and laptop)"""
    
    def __init__(self, camera_id: int, camera_type: str, rtsp_url: Optional[str] = None, camera_index: Optional[int] = None):
        self.camera_id = camera_id
        self.camera_type = camera_type
        self.rtsp_url = rtsp_url
        self.camera_index = camera_index
        self.cap: Optional[cv2.VideoCapture] = None
        self.reconnect_attempts = 0
        self.is_connected = False
    
    def connect(self) -> bool:
        """Connect to camera"""
        try:
            if self.camera_type == "rtsp":
                if not self.rtsp_url:
                    logger.error(f"Camera {self.camera_id}: RTSP URL not provided")
                    return False
                
                logger.info(f"Camera {self.camera_id}: Connecting to RTSP stream: {self.rtsp_url}")
                self.cap = cv2.VideoCapture(self.rtsp_url)
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce latency
                
            elif self.camera_type == "laptop":
                index = self.camera_index if self.camera_index is not None else LAPTOP_CAMERA_INDEX
                logger.info(f"Camera {self.camera_id}: Connecting to laptop camera index {index}")
                self.cap = cv2.VideoCapture(index)
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            else:
                logger.error(f"Camera {self.camera_id}: Unknown camera type: {self.camera_type}")
                return False
            
            # Test if camera is working
            if self.cap is None or not self.cap.isOpened():
                logger.error(f"Camera {self.camera_id}: Failed to open")
                self.disconnect()
                return False
            
            # Try to read a frame
            ret, frame = self.cap.read()
            if not ret or frame is None:
                logger.error(f"Camera {self.camera_id}: Failed to read frame")
                self.disconnect()
                return False
            
            self.is_connected = True
            self.reconnect_attempts = 0
            logger.info(f"Camera {self.camera_id}: Connected successfully")
            return True
            
        except Exception as e:
            logger.error(f"Camera {self.camera_id}: Connection error: {e}")
            self.disconnect()
            return False
    
    def disconnect(self):
        """Disconnect from camera"""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.is_connected = False
    
    def read_frame(self) -> Optional[Tuple[bool, any]]:
        """
        Read frame from camera
        
        Returns:
            (success, frame) tuple or None if disconnected
        """
        if not self.is_connected or self.cap is None:
            return None
        
        try:
            ret, frame = self.cap.read()
            
            if not ret or frame is None:
                # Camera disconnected or frame read failed
                logger.warning(f"Camera {self.camera_id}: Frame read failed, attempting reconnect...")
                self.is_connected = False
                return None
            
            return (ret, frame)
            
        except Exception as e:
            logger.error(f"Camera {self.camera_id}: Error reading frame: {e}")
            self.is_connected = False
            return None
    
    def reconnect(self) -> bool:
        """Attempt to reconnect to camera"""
        if self.reconnect_attempts >= MAX_RECONNECT_ATTEMPTS:
            logger.error(f"Camera {self.camera_id}: Max reconnect attempts reached")
            return False
        
        self.reconnect_attempts += 1
        logger.info(f"Camera {self.camera_id}: Reconnect attempt {self.reconnect_attempts}/{MAX_RECONNECT_ATTEMPTS}")
        
        self.disconnect()
        time.sleep(RECONNECT_DELAY)
        
        return self.connect()
    
    def get_info(self) -> dict:
        """Get camera information"""
        return {
            "camera_id": self.camera_id,
            "camera_type": self.camera_type,
            "rtsp_url": self.rtsp_url,
            "camera_index": self.camera_index,
            "is_connected": self.is_connected,
            "reconnect_attempts": self.reconnect_attempts
        }


def create_camera_managers() -> list[CameraManager]:
    """
    Create camera managers from configuration (DEPRECATED)
    
    Note: This function is no longer used by VideoWorker.
    VideoWorker now uses cameras from database only.
    Kept for backward compatibility.
    """
    managers = []
    
    # RTSP cameras (deprecated - use database instead)
    for idx, rtsp_url in enumerate(RTSP_CAMERAS):
        manager = CameraManager(
            camera_id=idx + 1,
            camera_type="rtsp",
            rtsp_url=rtsp_url
        )
        managers.append(manager)
    
    # Laptop camera (if enabled)
    if USE_LAPTOP_CAMERA:
        laptop_id = len(RTSP_CAMERAS) + 1
        manager = CameraManager(
            camera_id=laptop_id,
            camera_type="laptop",
            camera_index=LAPTOP_CAMERA_INDEX
        )
        managers.append(manager)
    
    return managers

