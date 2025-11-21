# Frontend - Face Recognition Attendance System

Next.js frontend for the face recognition attendance system.

## Features

- ✅ Real-time attendance monitoring via WebSocket
- ✅ Student management (add, delete, upload faces)
- ✅ Attendance statistics and charts
- ✅ Camera status monitoring
- ✅ Responsive design

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create `.env.local` file:
```bash
cp .env.local.example .env.local
```

3. Configure environment variables:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

4. Run development server:
```bash
npm run dev
```

5. Open http://localhost:3000

## Components

- **StudentsList**: Manage students (add, delete, upload faces)
- **AttendanceList**: Real-time attendance logs with WebSocket
- **AttendanceStats**: Statistics and charts
- **CameraStatus**: Camera monitoring
- **AddStudentModal**: Add new student
- **UploadFaceModal**: Upload face image from file
- **CameraFaceUpload**: Upload face image from camera

## API Integration

All API calls are handled through `/lib/api.ts`:
- Students API
- Attendance API
- Upload API

WebSocket connection is managed in `/lib/websocket.ts`.

