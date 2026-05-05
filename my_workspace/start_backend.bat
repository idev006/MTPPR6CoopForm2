@echo off
title CoopForm Backend (Dev)
echo ==============================
echo  CoopForm Backend - Dev Mode
echo ==============================
echo.

:: Kill any process on port 8000 before starting
echo Checking port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000 " ^| findstr "LISTENING"') do (
    echo Killing old process PID %%a ...
    taskkill /F /PID %%a /T >nul 2>&1
)
timeout /t 1 /nobreak >nul

call F:\programming\python\MTPPR6CoopForm2\Scripts\activate

cd /d F:\programming\python\MTPPR6CoopForm2\my_workspace\backend

set "PYTHONUTF8=1"

echo.
echo Starting uvicorn at http://localhost:8000
echo Press Ctrl+C to stop
echo.

uvicorn app.main:app --reload

pause
