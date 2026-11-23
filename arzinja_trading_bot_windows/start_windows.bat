@echo off
setlocal
set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

if not exist "%PROJECT_ROOT%.venv\Scripts\python.exe" (
  echo ابتدا install_windows.ps1 را با PowerShell اجرا کن.
  pause
  exit /b 1
)
if not exist "%PROJECT_ROOT%frontend\node_modules" (
  echo ابتدا install_windows.ps1 را اجرا کن.
  pause
  exit /b 1
)
if not exist "%PROJECT_ROOT%start_backend.bat" (
  echo فایل start_backend.bat پیدا نشد.
  pause
  exit /b 1
)

start "Arzinja API - PAPER" cmd /k "call ""%PROJECT_ROOT%start_backend.bat"""
timeout /t 3 /nobreak >nul
start "Arzinja Dashboard" cmd /k "cd /d ""%PROJECT_ROOT%frontend"" && npm run dev"
timeout /t 3 /nobreak >nul
start "" "http://127.0.0.1:5173"
endlocal
