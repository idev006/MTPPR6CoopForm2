@echo off
:: ============================================================
::  CoopForm — PostgreSQL First-Time Setup
::
::  สิ่งที่ทำ:
::    1. Start PostgreSQL container (ถ้ายังไม่รัน)
::    2. รัน alembic upgrade head (สร้าง 10 ตาราง)
::    3. รัน seed_dev.py (สร้าง borrower + staff)
::
::  Prerequisite: Docker Desktop ต้องเปิดอยู่
:: ============================================================

title CoopForm — PostgreSQL Setup

set PG_CONTAINER=coopform-pg
set PG_IMAGE=postgres:16-alpine
set PG_DB=coopform
set PG_USER=coopuser
set PG_PASS=coopdev123
set PG_PORT=5432

set "DATABASE_URL=postgresql+asyncpg://%PG_USER%:%PG_PASS%@localhost:%PG_PORT%/%PG_DB%"
set "SECRET_KEY=dev_secret_key_change_me_in_production_32ch"
set "REFRESH_TOKEN_SECRET=dev_refresh_key_change_me_in_production_32ch"
set "CONFIG_DIR=F:\programming\python\MTPPR6CoopForm2\my_workspace\config"
set "ENVIRONMENT=development"
set "PYTHONUTF8=1"

echo =====================================================
echo   CoopForm — PostgreSQL Setup
echo =====================================================
echo.

:: ── Step 1: Check Docker ──────────────────────────────────────
echo [1/3] Checking Docker...
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running. Start Docker Desktop first.
    pause & exit /b 1
)
echo       Docker OK

:: ── Step 2: Start or reuse PostgreSQL container ───────────────
echo.
echo [2/3] Starting PostgreSQL container "%PG_CONTAINER%"...

:: Check if container already exists
docker inspect %PG_CONTAINER% >nul 2>&1
if errorlevel 1 (
    echo       Creating new container...
    docker run -d --name %PG_CONTAINER% ^
        -e POSTGRES_DB=%PG_DB% ^
        -e POSTGRES_USER=%PG_USER% ^
        -e POSTGRES_PASSWORD=%PG_PASS% ^
        -p %PG_PORT%:5432 ^
        %PG_IMAGE%
) else (
    :: Container exists — check if it's running
    for /f "delims=" %%s in ('docker inspect -f "{{.State.Running}}" %PG_CONTAINER% 2^>nul') do set PG_RUNNING=%%s
    if "%PG_RUNNING%"=="false" (
        echo       Restarting existing container...
        docker start %PG_CONTAINER%
    ) else (
        echo       Container already running — skip
    )
)

:: Wait for PostgreSQL to be ready
echo       Waiting for PostgreSQL to be ready...
:wait_loop
timeout /t 2 /nobreak >nul
docker exec %PG_CONTAINER% pg_isready -U %PG_USER% -d %PG_DB% >nul 2>&1
if errorlevel 1 goto wait_loop
echo       PostgreSQL ready!

:: ── Step 3: Alembic migrations ────────────────────────────────
echo.
echo [3/3] Running alembic upgrade head...
call F:\programming\python\MTPPR6CoopForm2\Scripts\activate
cd /d F:\programming\python\MTPPR6CoopForm2\my_workspace\backend

python -m alembic upgrade head
if errorlevel 1 (
    echo [ERROR] Alembic migration failed!
    pause & exit /b 1
)
echo       Migrations applied!

:: ── Step 4: Seed users ────────────────────────────────────────
echo.
echo [4/4] Seeding dev users...
python seed_dev.py
if errorlevel 1 (
    echo [WARN] Seed may have failed ^(OK if users already exist^)
)

echo.
echo =====================================================
echo   Setup complete!
echo =====================================================
echo.
echo   Host    : localhost:%PG_PORT%
echo   Database: %PG_DB%
echo   User    : %PG_USER% / %PG_PASS%
echo.
echo   Start backend with:  run_backend.bat postgres
echo   Start all dev:       start_dev.bat postgres
echo.
pause
