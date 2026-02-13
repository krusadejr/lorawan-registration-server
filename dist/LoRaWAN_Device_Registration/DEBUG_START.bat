@echo off
REM Debug startup script - shows all errors
REM This script is for troubleshooting

title LoRaWAN Device Registration - DEBUG MODE
color 0C

echo.
echo ====================================================================
echo   LoRaWAN Device Registration - DEBUG MODE
echo ====================================================================
echo.
echo This window will show all errors and debug information.
echo If the program crashes, you will see the error messages here.
echo.
echo Please share any error messages you see with support.
echo.
echo ====================================================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Show detailed error information
echo Attempting to start application...
echo Current directory: %cd%
echo.

REM Run with error output
LoRaWAN_Device_Registration.exe

REM If we get here, the app crashed
echo.
echo ====================================================================
echo ERROR: Application exited unexpectedly
echo Please check the console output above for error messages
echo ====================================================================
echo.
pause
