#!/bin/bash
# Startup script for Face Recognition Attendance System

echo "Starting Face Recognition Attendance System..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "Warning: .env file not found. Copying from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "Please edit .env file with your configuration"
    fi
fi

# Start backend
echo "Starting backend..."
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start video worker
echo "Starting video worker..."
cd backend
python -m video_worker.main &
WORKER_PID=$!
cd ..

# Start frontend
echo "Starting frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo "All services started!"
echo "Backend PID: $BACKEND_PID"
echo "Video Worker PID: $WORKER_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap "kill $BACKEND_PID $WORKER_PID $FRONTEND_PID; exit" INT TERM
wait

