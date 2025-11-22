# Environment Configuration Guide

## Quick Setup

### Backend
```bash
cd backend
cp ../env.example .env
# Edit .env with your settings
```

### Frontend
```bash
cd frontend
cp ../env.example .env.local
# Edit .env.local with your settings
```

## Environment Variables

### Backend Variables

#### API Settings
- `API_HOST` - API server host (default: `0.0.0.0`)
- `API_PORT` - API server port (default: `8000`)
- `API_URL` - Full API URL (default: `http://localhost:8000`)
- `AUTO_START_VIDEO_WORKER` - Auto-start video worker on startup (default: `true`)

#### Directories
- `DATA_DIR` - Data directory path (default: `./data`)
- `MODEL_DIR` - Model directory path (default: `./models`)
- `DB_DIR` - Database directory path (default: `./data`)
- `DETECTED_FACES_DIR` - Detected faces directory (default: `./data/detected_faces`)

#### Face Recognition
- `MODEL_NAME` - InsightFace model name (default: `buffalo_l`)
- `FACE_RECOGNITION_THRESHOLD` - Recognition threshold 0.0-1.0 (default: `0.4`)
- `FACE_DETECTION_THRESHOLD` - Detection threshold 0.0-1.0 (default: `0.5`)
- `USE_GPU` - Enable GPU acceleration (default: `false`)

#### Camera Configuration
- `RTSP_CAMERAS` - **DEPRECATED**: Video worker now uses ONLY cameras from database. Configure cameras via admin panel (Admin → RTSP Config).
- `USE_LAPTOP_CAMERA` - Enable laptop camera (default: `false`)
- `LAPTOP_CAMERA_INDEX` - Laptop camera index (default: `0`)

#### Video Worker
- `FRAME_SKIP` - Process every Nth frame (default: `2`)
- `DUPLICATE_PREVENTION_WINDOW_SECONDS` - Duplicate prevention window (default: `60`)
- `DEEPSORT_ENABLED` - Enable DeepSORT tracking (default: `false`)
- `RECONNECT_DELAY` - Camera reconnection delay in seconds (default: `5`)
- `MAX_RECONNECT_ATTEMPTS` - Max reconnection attempts (default: `10`)

#### CORS
- `CORS_ORIGINS` - Comma-separated allowed origins (default: `http://localhost:3000`)

### Frontend Variables

#### Public Variables (must start with `NEXT_PUBLIC_`)
- `NEXT_PUBLIC_API_URL` - Backend API URL (default: `http://localhost:8000`)
- `NEXT_PUBLIC_WS_URL` - WebSocket URL (default: `ws://localhost:8000`)

## Example Configurations

### Development
```bash
# Backend .env
API_HOST=0.0.0.0
API_PORT=8000
USE_LAPTOP_CAMERA=false
USE_GPU=false
CORS_ORIGINS=http://localhost:3000

# Frontend .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### Production
```bash
# Backend .env
API_HOST=0.0.0.0
API_PORT=8000
API_URL=https://api.yourdomain.com
USE_LAPTOP_CAMERA=false
USE_GPU=true
DEEPSORT_ENABLED=true
CORS_ORIGINS=https://yourdomain.com

# Frontend .env.local
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_WS_URL=wss://api.yourdomain.com
```

### With Laptop Camera
```bash
# Backend .env
USE_LAPTOP_CAMERA=true
LAPTOP_CAMERA_INDEX=0
```

## Important Notes

1. **Video Worker**: Uses ONLY active RTSP cameras from database. Configure via admin panel.

2. **Laptop Camera**: Disabled by default. Set `USE_LAPTOP_CAMERA=true` to enable.

3. **GPU Support**: Requires NVIDIA GPU, CUDA, and `onnxruntime-gpu` package.

4. **DeepSORT**: Requires `pip install deepsort-realtime` and `DEEPSORT_ENABLED=true`.

5. **Frontend Variables**: Only variables starting with `NEXT_PUBLIC_` are accessible in browser.

6. **Security**: Never commit `.env` files to git. Use `.env.example` as template.

