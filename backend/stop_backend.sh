#!/bin/bash
# Backend ni to'xtatish scripti

echo "🛑 Backend ni to'xtatish..."

# Uvicorn process'larni to'xtatish
echo "1. Uvicorn process'larni to'xtatish..."
pkill -f "uvicorn.*app.main" 2>/dev/null
sleep 1

# Port 8000 ni band qilgan process'larni to'xtatish
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "2. Port 8000 ni band qilgan process'larni to'xtatish..."
    kill -9 $(lsof -ti:8000) 2>/dev/null
    sleep 1
fi

# Tekshirish
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "⚠️  Port 8000 hali ham band"
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    sleep 1
fi

# Final tekshirish
if ! lsof -ti:8000 > /dev/null 2>&1; then
    echo "✅ Backend to'xtatildi!"
else
    echo "❌ Backend to'xtatilmadi, qo'lda tekshiring:"
    echo "   lsof -ti:8000 | xargs kill -9"
fi
