@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo ابتدا install_windows.ps1 را با PowerShell اجرا کن.
  pause
  exit /b 1
)
if not exist "frontend\node_modules" (
  echo ابتدا install_windows.ps1 را اجرا کن.
  pause
  exit /b 1
)
start "Arzinja API" cmd /k "cd /d ""%CD%\backend"" && ""%CD%\.venv\Scripts\python.exe"" -m uvicorn app.main:app --host 127.0.0.1 --port 8000"
timeout /t 2 /nobreak >nul
start "Arzinja Dashboard" cmd /k "cd /d ""%CD%\frontend"" && npm run dev"
timeout /t 3 /nobreak >nul
start "" "http://127.0.0.1:5173"
endlocal
