@echo off
REM ==========================================
REM Fake News Detector - Web Frontend Startup
REM ==========================================

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║        🔍 FAKE NEWS DETECTOR - WEB FRONTEND                   ║
echo ║                  Starting Server...                            ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Check if we're in the right directory
if not exist "app.py" (
    echo ❌ ERROR: app.py not found
    echo Please run this from: d:\projects\Fake news detector
    pause
    exit /b 1
)

echo ✅ Project files found
echo.

REM Install/update Flask if needed
echo 📦 Checking Flask installation...
python -m pip show Flask >nul 2>&1
if errorlevel 1 (
    echo Installing Flask...
    python -m pip install Flask Flask-CORS requests
    if errorlevel 1 (
        echo ❌ Failed to install Flask
        pause
        exit /b 1
    )
)

echo ✅ Flask is ready
echo.

REM Start the Flask server
echo 🚀 Starting Flask server...
echo.
echo ────────────────────────────────────────────────────────────────
echo   🌐 Open your browser and go to: http://127.0.0.1:5000
echo   
echo   📝 You can now:
echo      • Check fake news claims
echo      • Verify URLs
echo      • Get instant verdicts with fact-checking
echo
echo   ⌨️  Press Ctrl+C to stop the server
echo ────────────────────────────────────────────────────────────────
echo.

python app.py

if errorlevel 1 (
    echo.
    echo ❌ Error running Flask server
    pause
    exit /b 1
)
