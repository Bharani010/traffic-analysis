@echo off
echo ==============================================
echo Starting Traffic Analysis Platform Locally
echo ==============================================

REM Kill any process already running on port 8000
FOR /F "tokens=5 delims= " %%P IN ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') DO (
    echo Killing existing process on port 8000 (PID: %%P)...
    taskkill /PID %%P /F >nul 2>&1
)

REM Load .env file from project root
IF EXIST .env (
    FOR /F "usebackq eol=# tokens=1,* delims==" %%A IN (".env") DO (
        IF NOT "%%A"=="" (
            SET "%%A=%%B"
        )
    )
    echo Loaded environment from .env
) ELSE (
    echo WARNING: .env file not found. Copy .env.example to .env and add your keys.
)

echo.
echo Starting FastAPI Backend on port 8000...
cd backend
start /B uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
cd ..

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

echo Starting React Frontend on port 3000...
echo.
echo Dashboard will be at: http://localhost:3000
echo API Docs will be at:  http://localhost:8000/api/docs
echo.
cd frontend
npm run dev -- --port 3000
