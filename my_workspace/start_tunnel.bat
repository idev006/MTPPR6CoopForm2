@echo off
title CoopForm - Cloudflare Tunnel

echo ==============================
echo   CoopForm - Cloudflare Tunnel
echo ==============================
echo.

:: 1. Locate cloudflared.exe
set CF=C:\Program Files ^(x86^)\cloudflared\cloudflared.exe
if exist "%CF%" goto :cf_found

set CF=C:\Program Files\cloudflared\cloudflared.exe
if exist "%CF%" goto :cf_found

for /f "delims=" %%i in ('where cloudflared 2^>nul') do (
    set CF=%%i
    goto :cf_found
)

echo [ERROR] cloudflared not found.
echo   Expected: C:\Program Files (x86)\cloudflared\cloudflared.exe
echo   Fix: winget install Cloudflare.cloudflared
pause
exit /b 1

:cf_found
echo   cloudflared : %CF%
echo.

:: 2. Check backend port 8000
echo Checking dev servers...
netstat -ano | findstr ":8000 " | findstr "LISTENING" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [WARN] Backend port 8000 is not running.
    echo        Please run start_dev.bat first.
    echo.
    choice /c YN /m "Open start_dev.bat now? (Y/N)"
    if %errorlevel% equ 2 ( pause & exit /b 1 )
    start "" "%~dp0start_dev.bat"
    echo Waiting 15s for servers to start...
    timeout /t 15 /nobreak >nul
)

:: 3. Check frontend port 5173
netstat -ano | findstr ":5173 " | findstr "LISTENING" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [WARN] Frontend port 5173 is not running.
    echo        Please wait for Vite dev server to start.
    echo.
    pause
    exit /b 1
)

echo   Backend  : OK (port 8000)
echo   Frontend : OK (port 5173)
echo.

:: 4. Start Cloudflare Quick Tunnel
echo ==============================
echo   Starting Cloudflare Tunnel
echo   Tunnel -^> http://localhost:5173
echo ==============================
echo.
echo   Public URL will appear below:
echo   https://xxxx-xxxx-xxxx.trycloudflare.com
echo.
echo   Share that URL with users on the internet.
echo   Close this window to stop the tunnel.
echo.
echo ==============================
echo.

"%CF%" tunnel --url http://localhost:5173

echo.
echo Tunnel stopped.
pause
