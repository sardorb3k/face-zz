#!/usr/bin/env python3
"""
FastAPI application runner
"""
import uvicorn
import threading
import sys
import signal
import time
from app.background_tasks import stop_video_worker

# Global flag for shutdown
shutdown_flag = threading.Event()
uvicorn_server = None

def run_uvicorn():
    """Run uvicorn server in a separate thread"""
    global uvicorn_server
    try:
        config = uvicorn.Config(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True
        )
        uvicorn_server = uvicorn.Server(config)
        uvicorn_server.run()
    except Exception as e:
        print(f"Uvicorn xatolik: {e}")

def signal_handler(sig, frame):
    """Handle CTRL+C"""
    print("\n🛑 Backend to'xtatilmoqda...")
    shutdown_flag.set()
    # Stop video worker
    try:
        stop_video_worker()
    except:
        pass
    # Stop uvicorn server
    if uvicorn_server:
        uvicorn_server.should_exit = True
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handler for CTRL+C
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Print instructions
    print("\n" + "="*60)
    print("✅ Backend ishga tushmoqda...")
    print("📝 To'xtatish uchun 'q' ni bosing va Enter ni bosing")
    print("📝 Yoki CTRL+C ni bosing")
    print("="*60 + "\n")
    
    # Start uvicorn in a separate thread
    uvicorn_thread = threading.Thread(target=run_uvicorn, daemon=False)
    uvicorn_thread.start()
    
    # Wait a bit for server to start
    time.sleep(2)
    
    # Main thread: listen for 'q' input
    try:
        while not shutdown_flag.is_set():
            try:
                user_input = input().strip().lower()
                if user_input == 'q':
                    print("\n🛑 Backend to'xtatilmoqda...")
                    shutdown_flag.set()
                    # Stop video worker
                    try:
                        stop_video_worker()
                    except:
                        pass
                    # Stop uvicorn server
                    if uvicorn_server:
                        uvicorn_server.should_exit = True
                    break
            except (EOFError, KeyboardInterrupt):
                break
            except Exception:
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n🛑 Backend to'xtatildi")
        shutdown_flag.set()
        try:
            stop_video_worker()
        except:
            pass
    
    # Wait for uvicorn thread to finish
    if uvicorn_thread.is_alive():
        uvicorn_thread.join(timeout=5)

