@echo off
REM ========================================
REM LoRaWAN Device Registration Server
REM Easy Start Script
REM ========================================

echo.
echo ========================================
echo  LoRaWAN Device Registration Server
echo ========================================
echo.
echo Starting application...
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if activation was successful
if errorlevel 1 (
    echo ERROR: Could not activate virtual environment!
    echo Please make sure the virtual environment exists in the 'venv' folder.
    echo.
    pause
    exit /b 1
)

echo Virtual environment activated.
echo.

REM Start the Flask application
echo Starting Flask server...
echo The application will be available at: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python app.py

REM If Python exits with an error, pause so user can see the error
if errorlevel 1 (
    echo.
    echo ========================================
    echo ERROR: Application stopped with an error!
    echo ========================================
    pause
)
