$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
  throw "Python پیدا نشد. Python 3.11 یا جدیدتر را نصب و دوباره اجرا کن."
}
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
  throw "Node.js و npm پیدا نشدند. نسخه LTS را نصب کن."
}

if (-not (Test-Path ".venv")) { python -m venv .venv }
& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\python.exe" -m pip install -r backend\requirements.txt
Set-Location frontend
npm install
Set-Location $Root
if (-not (Test-Path ".env")) { Copy-Item ".env.example" ".env" }
Write-Host "نصب اولیه کامل شد. برای اجرا start_windows.bat را اجرا کن." -ForegroundColor Green
