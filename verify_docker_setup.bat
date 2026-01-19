@echo off
REM ============================================================================
REM Arc BaaS - Docker Setup Verification Script (Windows)
REM ============================================================================

echo ========================================
echo Arc BaaS - Docker Setup Verification
echo ========================================
echo.

set ERRORS=0
set WARNINGS=0

REM ----------------------------------------------------------------------------
REM Check Prerequisites
REM ----------------------------------------------------------------------------
echo [1/6] Checking Prerequisites...

where docker >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] docker found
) else (
    echo [ERROR] docker not found
    set /a ERRORS+=1
)

where docker-compose >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] docker-compose found
) else (
    echo [ERROR] docker-compose not found
    set /a ERRORS+=1
)
echo.

REM ----------------------------------------------------------------------------
REM Check Core Docker Files
REM ----------------------------------------------------------------------------
echo [2/6] Checking Core Docker Files...

if exist Dockerfile (echo [OK] Dockerfile) else (echo [ERROR] Dockerfile MISSING & set /a ERRORS+=1)
if exist Dockerfile.frontend (echo [OK] Dockerfile.frontend) else (echo [ERROR] Dockerfile.frontend MISSING & set /a ERRORS+=1)
if exist docker-compose.yml (echo [OK] docker-compose.yml) else (echo [ERROR] docker-compose.yml MISSING & set /a ERRORS+=1)
if exist docker-compose.monitoring.yml (echo [OK] docker-compose.monitoring.yml) else (echo [ERROR] docker-compose.monitoring.yml MISSING & set /a ERRORS+=1)
if exist .dockerignore (echo [OK] .dockerignore) else (echo [ERROR] .dockerignore MISSING & set /a ERRORS+=1)
if exist docker-entrypoint.sh (echo [OK] docker-entrypoint.sh) else (echo [ERROR] docker-entrypoint.sh MISSING & set /a ERRORS+=1)
echo.

REM ----------------------------------------------------------------------------
REM Check Configuration Files
REM ----------------------------------------------------------------------------
echo [3/6] Checking Configuration Files...

if exist .env.example (echo [OK] .env.example) else (echo [ERROR] .env.example MISSING & set /a ERRORS+=1)
if exist .env.docker (echo [OK] .env.docker) else (echo [ERROR] .env.docker MISSING & set /a ERRORS+=1)
if exist requirements.txt (echo [OK] requirements.txt) else (echo [ERROR] requirements.txt MISSING & set /a ERRORS+=1)
if exist Makefile (echo [OK] Makefile) else (echo [WARNING] Makefile MISSING & set /a WARNINGS+=1)

if exist .env (
    echo [OK] .env
    echo.
    echo Checking .env contents...
    findstr /C:"CIRCLE_API_KEY" .env >nul && echo [OK] CIRCLE_API_KEY found || echo [ERROR] CIRCLE_API_KEY not found & set /a ERRORS+=1
    findstr /C:"GEMINI_API_KEY" .env >nul && echo [OK] GEMINI_API_KEY found || echo [ERROR] GEMINI_API_KEY not found & set /a ERRORS+=1
    findstr /C:"PRIVATE_KEY" .env >nul && echo [OK] PRIVATE_KEY found || echo [ERROR] PRIVATE_KEY not found & set /a ERRORS+=1
) else (
    echo [WARNING] .env MISSING - copy from .env.docker
    set /a WARNINGS+=1
)
echo.

REM ----------------------------------------------------------------------------
REM Check Docker Directory Structure
REM ----------------------------------------------------------------------------
echo [4/6] Checking Docker Directory Structure...

if exist docker\ (echo [OK] docker\) else (echo [ERROR] docker\ MISSING & set /a ERRORS+=1)
if exist docker\init-scripts\ (echo [OK] docker\init-scripts\) else (echo [WARNING] docker\init-scripts\ MISSING & set /a WARNINGS+=1)
if exist docker\volumes\ (echo [OK] docker\volumes\) else (echo [WARNING] docker\volumes\ MISSING & set /a WARNINGS+=1)
if exist docker\volumes\postgres\ (echo [OK] docker\volumes\postgres\) else (echo [WARNING] docker\volumes\postgres\ MISSING & set /a WARNINGS+=1)
if exist docker\volumes\redis\ (echo [OK] docker\volumes\redis\) else (echo [WARNING] docker\volumes\redis\ MISSING & set /a WARNINGS+=1)
if exist docker\prometheus\ (echo [OK] docker\prometheus\) else (echo [WARNING] docker\prometheus\ MISSING & set /a WARNINGS+=1)
if exist docker\grafana\ (echo [OK] docker\grafana\) else (echo [WARNING] docker\grafana\ MISSING & set /a WARNINGS+=1)
echo.

REM ----------------------------------------------------------------------------
REM Check Application Directories
REM ----------------------------------------------------------------------------
echo [5/6] Checking Application Directories...

if exist banking_data\ (echo [OK] banking_data\) else (echo [WARNING] banking_data\ MISSING & set /a WARNINGS+=1)
if exist logs\ (echo [OK] logs\) else (echo [WARNING] logs\ MISSING & set /a WARNINGS+=1)
if exist memory\ (echo [OK] memory\) else (echo [WARNING] memory\ MISSING & set /a WARNINGS+=1)
if exist outputs\ (echo [OK] outputs\) else (echo [WARNING] outputs\ MISSING & set /a WARNINGS+=1)
echo.

REM ----------------------------------------------------------------------------
REM Check Main Application Files
REM ----------------------------------------------------------------------------
echo [6/6] Checking Main Application Files...

if exist baas_backend.py (echo [OK] baas_backend.py) else (echo [ERROR] baas_backend.py MISSING & set /a ERRORS+=1)
if exist banking_ui_professional.py (echo [OK] banking_ui_professional.py) else (echo [ERROR] banking_ui_professional.py MISSING & set /a ERRORS+=1)
if exist banking_syndicate.py (echo [OK] banking_syndicate.py) else (echo [ERROR] banking_syndicate.py MISSING & set /a ERRORS+=1)
echo.

REM ----------------------------------------------------------------------------
REM Summary
REM ----------------------------------------------------------------------------
echo ========================================
echo Verification Summary
echo ========================================

if %ERRORS% EQU 0 (
    if %WARNINGS% EQU 0 (
        echo [SUCCESS] All checks passed!
        echo.
        echo Ready to deploy:
        echo   1. Edit .env with your API keys
        echo   2. Run: docker-compose build
        echo   3. Run: docker-compose up -d
        echo   4. Check: docker-compose ps
    ) else (
        echo [WARNING] %WARNINGS% warning(s)
        echo.
        echo Warnings can usually be ignored.
        echo Missing directories will be created automatically.
    )
) else (
    echo [ERROR] %ERRORS% error(s)
    echo [WARNING] %WARNINGS% warning(s)
    echo.
    echo Please fix errors before deploying.
)

echo.
echo Next Steps:
echo   1. Set API keys in .env file
echo   2. Run: docker-compose build
echo   3. Run: docker-compose up -d
echo   4. Check: docker-compose ps
echo.
echo Documentation:
echo   - Quick Start: DOCKER_QUICKSTART.md
echo   - Full Guide: docker\README.md
echo   - Summary: DOCKER_DEPLOYMENT_SUMMARY.md
echo.

pause
