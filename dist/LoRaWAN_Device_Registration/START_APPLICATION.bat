@echo off
REM ====================================================================
REM   LoRaWAN Device Registration Server
REM ====================================================================

title LoRaWAN Device Registration Server
color 0A

echo.
echo ====================================================================
echo   LoRaWAN Device Registration Server
echo ====================================================================
echo.
echo Starting application...
echo Please wait while the server initializes (this may take 10-15 seconds on first run)
echo.
echo Once started, open your browser to: http://localhost:5000
echo.
echo If you see errors below, please note them and contact support.
echo.
echo Press CTRL+C to stop the server
echo ====================================================================
echo.

REM Change to script directory to ensure relative paths work
cd /d "%~dp0"

REM Run the executable and capture any errors
LoRaWAN_Device_Registration.exe

echo.
echo ====================================================================
echo Server stopped. You can close this window.
echo ====================================================================
timeout /t 5
