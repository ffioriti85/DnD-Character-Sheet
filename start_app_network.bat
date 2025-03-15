@echo off
title D&D Character Sheet App (Network Access)
echo Starting D&D Character Sheet Application with network access...
echo.

REM Set the specific Python path we found
SET PYTHON_CMD="C:\Users\ffior\AppData\Local\Programs\Python\Python313\python.exe"
SET PIP_CMD="C:\Users\ffior\AppData\Local\Programs\Python\Python313\Scripts\pip.exe"
SET FLASK_CMD="C:\Users\ffior\AppData\Local\Programs\Python\Python313\Scripts\flask.exe"

echo Found Python at: %PYTHON_CMD%
echo.

REM Check if Flask is installed
echo Checking for Flask installation...
%PYTHON_CMD% -c "import flask" 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo Installing required packages...
    %PIP_CMD% install flask flask-bootstrap flask-ckeditor flask-sqlalchemy
)
echo Flask is installed.
echo.

REM Get IP address
echo Getting network information...
FOR /F "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /R /C:"IPv4 Address"') do set IP=%%a
set IP=%IP:~1%

echo Your IP address is: %IP%
echo.
echo To access from another device on the same network, use:
echo http://%IP%:5000
echo.
echo Starting server...
echo.
echo Press Ctrl+C to stop the server
echo.

REM Create a temporary Python script to run Flask with host 0.0.0.0
echo from app import app > run_network.py
echo if __name__ == '__main__': >> run_network.py
echo     app.run(host='0.0.0.0', port=5000, debug=True) >> run_network.py

REM Start the Flask application
%PYTHON_CMD% run_network.py

REM Clean up
del run_network.py

echo.
echo Server stopped.
echo.
pause 