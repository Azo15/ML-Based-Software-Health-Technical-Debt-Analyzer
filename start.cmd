@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Local environment not found. Follow docs\QUICKSTART_TR.md first.
  exit /b 1
)
git --version >nul 2>&1
if errorlevel 1 (
  echo Git is not installed or is not on PATH.
  exit /b 1
)
".venv\Scripts\python.exe" -m web %*
exit /b %errorlevel%
