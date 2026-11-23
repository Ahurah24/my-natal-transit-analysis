@echo off
setlocal
set "PROJECT_ROOT=%~dp0"

if not exist "%PROJECT_ROOT%.venv\Scripts\python.exe" (
  echo Python virtual environment not found: "%PROJECT_ROOT%.venv\Scripts\python.exe"
  echo Run install_windows.ps1 from the project folder first.
  pause
  exit /b 1
)

pushd "%PROJECT_ROOT%backend"
echo Starting Arzinja FastAPI backend in PAPER mode...
echo API: http://127.0.0.1:8000
echo API docs: http://127.0.0.1:8000/docs
"%PROJECT_ROOT%.venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000
set "EXIT_CODE=%ERRORLEVEL%"
popd

if not "%EXIT_CODE%"=="0" (
  echo Backend exited with code %EXIT_CODE%.
  pause
)
exit /b %EXIT_CODE%
