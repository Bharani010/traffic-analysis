@echo off
echo ==============================================
echo Running Data Engineering Pipeline
echo ==============================================

echo.
echo [1/3] Simulating Traffic...
python -m data.jobs.simulate_traffic
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Simulation failed.
    exit /b %ERRORLEVEL%
)

echo.
echo [2/3] Running PySpark ETL...
python -m data.jobs.process_events
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] ETL failed.
    exit /b %ERRORLEVEL%
)

echo.
echo [3/3] Running Detection Engine...
python -m data.jobs.detect_anomalies
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Detection engine failed.
    exit /b %ERRORLEVEL%
)

echo.
echo ==============================================
echo Pipeline complete! You can now start the backend
echo and view the dashboard to see the anomalies.
echo ==============================================
