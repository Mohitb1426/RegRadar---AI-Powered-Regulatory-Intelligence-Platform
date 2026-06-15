@echo off
echo ========================================
echo Starting RegRadar Complete System
echo ========================================
echo.

echo [1/3] Checking environment...
if not exist .env (
    echo ERROR: .env file not found in root directory
    echo Please copy .env.example to .env and configure it
    pause
    exit /b 1
)

echo [2/3] Starting Backend API...
cd backend
start "RegRadar Backend" cmd /k "python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
cd ..

echo Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo [3/3] Starting Frontend...
cd frontend
start "RegRadar Frontend" cmd /k "npm run dev"
cd ..

echo.
echo ========================================
echo RegRadar is starting!
echo ========================================
echo.
echo Backend API: http://localhost:8000
echo Frontend UI: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo Two windows will open:
echo 1. Backend (FastAPI) - Keep running
echo 2. Frontend (React) - Keep running
echo.
echo Press any key to open the application in your browser...
pause > nul

echo Opening browser...
start http://localhost:3000

echo.
echo System is running!
echo Close the backend and frontend windows to stop the servers.
