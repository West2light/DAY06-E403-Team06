@echo off
echo ====================================
echo   Vinmec AI Chatbot - Starting...
echo ====================================
cd /d "%~dp0backend"
pip install -r requirements.txt --quiet
echo.
echo Server dang chay tai: http://localhost:8000
echo Mo trinh duyet va truy cap: http://localhost:8000
echo Nhan Ctrl+C de dung server.
echo.
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
