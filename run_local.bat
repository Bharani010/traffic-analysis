@echo off
echo ==============================================
echo Starting Traffic Analysis Platform Locally
echo ==============================================

echo.
echo Starting FastAPI Backend (Port 8000)...
cd backend
start /B uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
cd ..

echo.
echo Starting React Frontend (Port 3000)...
cd frontend
npm run dev -- --port 3000

echo.
echo Closing this window will stop the frontend.
echo To stop the backend, you may need to close the Python process.
