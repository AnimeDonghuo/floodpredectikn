@echo off
setlocal
cd /d "%~dp0"
where docker >nul 2>nul
if errorlevel 1 (
  echo Docker is not installed or not in PATH.
  echo Install Docker Desktop, then run START.bat again.
  pause
  exit /b 1
)
echo Starting Geo Shield AI...
docker compose up --build
pause
