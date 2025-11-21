# Face Recognition Attendance System

Real-time face recognition attendance system for university entrance using SCRFD face detection, ArcFace recognition, and DeepSORT tracking.

## Architecture

- **Video Worker**: Processes RTSP/IP cameras and laptop camera
- **FastAPI Backend**: REST API + WebSocket for attendance management
- **SQLite Database**: Stores students, embeddings, and attendance logs
- **Next.js Frontend**: Admin panel with real-time WebSocket updates
- **Docker Compose**: Multi-service deployment with GPU support

## Features

- Real-time face detection using SCRFD 2.5G model
- Face recognition using ArcFace (InsightFace, r100) with 512-dim embeddings
- DeepSORT tracking per camera to prevent duplicates
- Duplicate prevention: 1-minute window per student per camera
- WebSocket real-time updates in admin panel
- Support for multiple RTSP cameras and laptop camera
- Average embeddings from 1-5 images per student
- Threshold: cosine similarity ≥ 0.4 for recognition

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose (for containerized deployment)
- NVIDIA GPU with CUDA (optional, for GPU acceleration)
- InsightFace models (buffalo_l recommended)

## Installation

### 1. Clone and Setup

```bash
cd face-r
```

### 2. Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

### 4. Environment Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env` with your settings:
- RTSP camera URLs
- API endpoints
- GPU settings
- Threshold values

## Running the System

### Development Mode

#### Backend
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Video Worker
```bash
cd backend
python -m video_worker.main
```

#### Frontend
```bash
cd frontend
npm run dev
```

### Docker Compose

```bash
docker-compose up -d
```

For GPU support, uncomment the `runtime: nvidia` line in `docker-compose.yml` and ensure NVIDIA Container Toolkit is installed.

## Usage

1. **Add Students**: Use the admin panel to add students and upload 1-5 face images per student
2. **Configure Cameras**: Add RTSP cameras or use laptop camera via admin panel or environment variables
3. **Start Video Worker**: The video worker will process frames, detect faces, recognize students, and log attendance
4. **Monitor**: View real-time attendance logs in the admin panel via WebSocket

## API Endpoints

- `GET /api/students` - List students
- `POST /api/students` - Create student
- `POST /api/upload/face` - Upload face image
- `GET /api/attendance` - Get attendance logs
- `GET /api/attendance/stats` - Get attendance statistics
- `WS /ws/attendance` - WebSocket for real-time updates

## Configuration

Key configuration options:

- `FACE_RECOGNITION_THRESHOLD`: Cosine similarity threshold (default: 0.4)
- `DUPLICATE_PREVENTION_WINDOW_SECONDS`: Time window for duplicate prevention (default: 60)
- `FRAME_SKIP`: Process every Nth frame (default: 2)
- `USE_GPU`: Enable GPU acceleration (default: false)
- `DEEPSORT_ENABLED`: Enable DeepSORT tracking (default: false - set to true if you want advanced tracking)

## Database

SQLite database is created automatically at `backend/data/attendance.db`. Schema includes:

- `students`: Student information
- `student_images`: Face images (1-5 per student)
- `student_embeddings`: Averaged embeddings
- `cameras`: Camera configuration
- `attendance_logs`: Attendance records

## Troubleshooting

### Camera Issues
- Check camera permissions: `sudo usermod -a -G video $USER`
- Verify RTSP URL format: `rtsp://username:password@ip:port/stream`
- Test camera connection: `ffplay rtsp://...`

### Model Issues
- Ensure InsightFace models are downloaded (buffalo_l recommended)
- Check model path in `MODEL_DIR` environment variable
- Verify GPU drivers if using GPU acceleration

### WebSocket Issues
- Check CORS settings in backend
- Verify WebSocket URL in frontend: `NEXT_PUBLIC_WS_URL`

## License

MIT

