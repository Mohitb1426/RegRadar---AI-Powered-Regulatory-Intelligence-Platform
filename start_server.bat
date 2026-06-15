@echo off
echo Starting RegRadar API Server...
echo.
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
