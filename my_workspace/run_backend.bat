@echo off
:: ============================================================
::  CoopForm Backend Launcher
::  Usage:
::    run_backend.bat              -- SQLite (default)
::    run_backend.bat sqlite       -- SQLite (explicit)
::    run_backend.bat postgres     -- PostgreSQL (local Docker)
::    run_backend.bat pg           -- PostgreSQL (alias)
:: ============================================================

title CoopForm Backend

set DB_MODE=sqlite
if /i "%~1"=="postgres" set DB_MODE=postgres
if /i "%~1"=="pg"       set DB_MODE=postgres

:: ── Set DATABASE_URL by mode ─────────────────────────────────
if "%DB_MODE%"=="postgres" (
    set "DATABASE_URL=postgresql+asyncpg://coopuser:coopdev123@localhost:5432/coopform"
    echo [DB] PostgreSQL  ^(localhost:5432/coopform^)
) else (
    set "DATABASE_URL=sqlite+aiosqlite:///./coopform_dev.db"
    echo [DB] SQLite  ^(coopform_dev.db^)
)

:: ── Activate venv ────────────────────────────────────────────
call F:\programming\python\MTPPR6CoopForm2\Scripts\activate

:: ── cd to backend ────────────────────────────────────────────
cd /d F:\programming\python\MTPPR6CoopForm2\my_workspace\backend

set "PYTHONUTF8=1"
set "SECRET_KEY=dev_secret_key_change_me_in_production_32ch"
set "REFRESH_TOKEN_SECRET=dev_refresh_key_change_me_in_production_32ch"
set "CONFIG_DIR=F:\programming\python\MTPPR6CoopForm2\my_workspace\config"
set "ENVIRONMENT=development"

:: ── Kill old process on port 8000 ────────────────────────────
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000 " ^| findstr "LISTENING" 2^>nul') do (
    taskkill /F /PID %%a /T >nul 2>&1
)
timeout /t 1 /nobreak >nul

echo.
echo  Starting uvicorn at http://localhost:8000
echo  Press Ctrl+C to stop
echo.

uvicorn app.main:app --reload

pause
