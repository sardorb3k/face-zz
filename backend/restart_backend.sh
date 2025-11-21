#!/bin/bash
# Backend ni qayta ishga tushirish scripti

echo "🔄 Backend ni qayta ishga tushirish..."

# Eski process'larni to'xtatish
echo "1. Eski process'larni to'xtatish..."
pkill -f "uvicorn.*app.main" 2>/dev/null
sleep 2

# Port tekshirish
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "⚠️  Port 8000 hali ham band, qo'shimcha to'xtatish..."
    kill -9 $(lsof -ti:8000) 2>/dev/null
    sleep 1
fi

# Backend ni ishga tushirish
echo "2. Backend ni ishga tushirish..."
cd "$(dirname "$0")"
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &

sleep 3

# Tekshirish
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend muvaffaqiyatli ishga tushdi!"
    echo "   URL: http://localhost:8000"
    echo "   Health: http://localhost:8000/health"
    echo "   Video Worker Status: http://localhost:8000/api/video-worker/status"
else
    echo "❌ Backend ishga tushmadi"
    exit 1
fi

