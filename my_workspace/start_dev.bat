@echo off
:: ============================================================
::  CoopForm Dev Launcher
::  Usage:
::    start_dev.bat              -- SQLite (default)
::    start_dev.bat postgres     -- PostgreSQL
::    start_dev.bat pg           -- PostgreSQL (alias)
:: ============================================================

title CoopForm Dev Launcher

set DB_MODE=sqlite
if /i "%~1"=="postgres" set DB_MODE=postgres
if /i "%~1"=="pg"       set DB_MODE=postgres

echo ==============================
echo   CoopForm - Start Dev Env
echo ==============================
echo.

if "%DB_MODE%"=="postgres" (
    echo   Database : PostgreSQL  ^(localhost:5432^)
    echo   Tip: run setup_postgres.bat first if first time
) else (
    echo   Database : SQLite  ^(coopform_dev.db^)
)
echo.

:: Guard: check venv
if not exist "F:\programming\python\MTPPR6CoopForm2\Scripts\activate" (
    echo [ERROR] venv not found. Run: python -m venv F:\programming\python\MTPPR6CoopForm2
    pause & exit /b 1
)

:: Guard: check node_modules
if not exist "F:\programming\python\MTPPR6CoopForm2\my_workspace\frontend\node_modules" (
    echo [ERROR] node_modules not found. Run: cd frontend ^&^& npm install
    pause & exit /b 1
)

:: Kill port 8000
echo Checking port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000 " ^| findstr "LISTENING"') do (
    echo   Killing PID %%a on port 8000...
    taskkill /F /PID %%a /T >nul 2>&1
)

:: Kill port 5173
echo Checking port 5173...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5173 " ^| findstr "LISTENING"') do (
    echo   Killing PID %%a on port 5173...
    taskkill /F /PID %%a /T >nul 2>&1
)

timeout /t 1 /nobreak >nul

echo.
echo Starting Backend  : http://localhost:8000  [%DB_MODE%]
start "CoopForm Backend" cmd /k "%~dp0run_backend.bat %DB_MODE%"

echo Starting Frontend : http://localhost:5173
timeout /t 5 /nobreak >nul
start "CoopForm Frontend" cmd /k "cd /d F:\programming\python\MTPPR6CoopForm2\my_workspace\frontend && npm run dev"

:: Wait for Vite then open browser
timeout /t 8 /nobreak >nul
start "" http://localhost:5173

echo.
echo ==============================
echo   Both servers are running
echo ==============================
echo.
echo   Backend  : http://localhost:8000
echo   Frontend : http://localhost:5173
echo   API Docs : http://localhost:8000/docs
echo.
echo   Login (Borrower) : borrower@coop.local / Test1234!
echo   Login (Staff)    : staff@coop.local    / Test1234!
echo.
echo   Close this window to keep servers running.
echo   To stop: close the Backend and Frontend windows.
echo.
pause
