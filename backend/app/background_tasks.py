"""
Background tasks for video worker
"""
import asyncio
import logging
import threading
from typing import Optional

logger = logging.getLogger(__name__)

# Global video worker thread and instance
_video_worker_thread: Optional[threading.Thread] = None
_video_worker_instance = None
_video_worker_running = False


def start_video_worker():
    """Start video worker in background thread"""
    global _video_worker_thread, _video_worker_running
    
    if _video_worker_running:
        logger.warning("Video worker allaqachon ishlayapti")
        return
    
    def run_worker():
        global _video_worker_running, _video_worker_instance
        try:
            logger.info("Video worker background thread ishga tushmoqda...")
            _video_worker_running = True
            
            # Import va ishga tushirish
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent))
            
            from video_worker.main import VideoWorker
            
            worker = VideoWorker()
            _video_worker_instance = worker
            worker.run()
        except Exception as e:
            logger.error(f"Video worker xatolik: {e}")
            import traceback
            traceback.print_exc()
        finally:
            _video_worker_running = False
            _video_worker_instance = None
            logger.info("Video worker to'xtatildi")
    
    _video_worker_thread = threading.Thread(target=run_worker, daemon=True)
    _video_worker_thread.start()
    logger.info("Video worker background thread yaratildi")


def stop_video_worker():
    """Stop video worker"""
    global _video_worker_running, _video_worker_instance
    
    if not _video_worker_running:
        logger.warning("Video worker ishlamayapti")
        return
    
    # Video worker ni to'xtatish
    if _video_worker_instance:
        _video_worker_instance.running = False
        logger.info("Video worker to'xtatish so'rovi yuborildi")
    else:
        _video_worker_running = False
        logger.info("Video worker to'xtatish so'rovi yuborildi")


def is_video_worker_running() -> bool:
    """Check if video worker is running"""
    return _video_worker_running and _video_worker_thread is not None and _video_worker_thread.is_alive()

