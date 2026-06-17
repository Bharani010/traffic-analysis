#!/usr/bin/env pwsh
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "  Traffic Analysis Platform - Local Startup" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan

# Kill anything on port 8000
$existing = netstat -ano | Select-String ":8000 " | Select-String "LISTENING"
if ($existing) {
    $pid8000 = ($existing -split '\s+')[-1]
    Write-Host "Freeing port 8000 (PID $pid8000)..." -ForegroundColor Yellow
    Stop-Process -Id $pid8000 -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
}

# Load .env file
$envFile = Join-Path $PSScriptRoot ".env"
if (Test-Path $envFile) {
    Write-Host "Loading .env file..." -ForegroundColor Green
    Get-Content $envFile | ForEach-Object {
        if ($_ -match "^\s*([^#][^=]+)=(.*)$") {
            [System.Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim(), "Process")
        }
    }
} else {
    Write-Host "WARNING: .env file not found! Copy .env.example to .env and add your GROQ_API_KEY." -ForegroundColor Red
}

Write-Host ""
Write-Host "Starting FastAPI Backend on http://localhost:8000 ..." -ForegroundColor Green
$backend = Start-Process -FilePath "uvicorn" `
    -ArgumentList "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload" `
    -WorkingDirectory (Join-Path $PSScriptRoot "backend") `
    -PassThru -NoNewWindow

Start-Sleep -Seconds 3
Write-Host "Backend PID: $($backend.Id)" -ForegroundColor Gray

Write-Host ""
Write-Host "Starting React Frontend on http://localhost:3000 ..." -ForegroundColor Green
Write-Host ""
Write-Host "  Dashboard -> http://localhost:3000" -ForegroundColor White
Write-Host "  API Docs  -> http://localhost:8000/api/docs" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop everything." -ForegroundColor Yellow
Write-Host ""

Set-Location (Join-Path $PSScriptRoot "frontend")
npx vite --port 3000

# When frontend stops, kill backend too
Stop-Process -Id $backend.Id -Force -ErrorAction SilentlyContinue
Write-Host "All services stopped." -ForegroundColor Cyan
