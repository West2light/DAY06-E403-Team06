#!/bin/bash
echo "===================================="
echo "  Vinmec AI Chatbot - Starting..."
echo "===================================="
cd "$(dirname "$0")/backend"
pip install -r requirements.txt -q
echo ""
echo "Server đang chạy tại: http://localhost:8000"
echo "Nhấn Ctrl+C để dừng."
echo ""
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
