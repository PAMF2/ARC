@echo off
REM Arc Hackathon Demo Runner (Windows)
REM Quick start script for the agentic commerce demo

echo ================================================================================
echo   ROCKET ARC HACKATHON DEMO - AGENTIC COMMERCE
echo   Powered by Circle Wallets + Arc Blockchain + Gemini AI
echo ================================================================================
echo.

REM Check Python version
echo MAGNIFYING GLASS Checking Python version...
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo X Python not found. Please install Python 3.10 or higher.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo CHECK Python %PYTHON_VERSION% detected
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    echo PACKAGE Creating virtual environment...
    python -m venv .venv
    echo CHECK Virtual environment created
    echo.
)

REM Activate virtual environment
echo WRENCH Activating virtual environment...
call .venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo X Failed to activate virtual environment
    pause
    exit /b 1
)
echo CHECK Virtual environment activated
echo.

REM Install dependencies
echo BOOKS Installing dependencies...
if exist "requirements.txt" (
    pip install -q -r requirements.txt
    echo CHECK Core dependencies installed
) else (
    echo WARNING requirements.txt not found
)
echo.

REM Check for optional Gemini AI
echo ROBOT Checking for Gemini AI...
python -c "import google.generativeai" >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo CHECK Gemini AI available
) else (
    echo WARNING Gemini AI not installed (demo will run in mock mode^)
    echo    Install with: pip install google-generativeai
)
echo.

REM Check for .env file
echo LOCK Checking configuration...
if exist ".env" (
    echo CHECK .env file found
) else (
    echo WARNING .env file not found (using defaults^)
    echo.
    echo To configure APIs, create .env with:
    echo   CIRCLE_API_KEY=your_circle_api_key
    echo   CIRCLE_ENTITY_SECRET=your_entity_secret
    echo   ARC_RPC_URL=https://rpc.arc.testnet.io
    echo   GEMINI_API_KEY=your_gemini_api_key
)
echo.

REM Display demo info
echo ================================================================================
echo   Demo Features:
echo     - AI agents with Circle Wallets
echo     - Autonomous USDC payments for API calls
echo     - Multi-agent consensus on transactions
echo     - Settlement on Arc blockchain
echo     - Gemini AI payment analytics
echo ================================================================================
echo.

REM Ask user if ready
pause

echo.
echo CLAPPER Starting demo...
echo.

REM Run the demo
python demo_arc_hackathon.py

REM Deactivate virtual environment
call deactivate

echo.
echo ================================================================================
echo   CHECK Demo completed!
echo ================================================================================
echo.
echo BOOKS Next steps:
echo   - Review HACKATHON_DEMO.md for detailed documentation
echo   - Configure real API keys in .env for production mode
echo   - Explore the code in demo_arc_hackathon.py
echo   - Star the repo if you found this useful!
echo.
pause
