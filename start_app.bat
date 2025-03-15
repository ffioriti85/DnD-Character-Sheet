@echo off
title D&D Character Sheet App
echo Starting D&D Character Sheet Application...
echo Please wait while the server starts...

REM Find Python in common installation locations
SET PYTHON_CMD=
IF EXIST "C:\Python39\python.exe" SET PYTHON_CMD="C:\Python39\python.exe"
IF EXIST "C:\Python310\python.exe" SET PYTHON_CMD="C:\Python310\python.exe"
IF EXIST "C:\Python311\python.exe" SET PYTHON_CMD="C:\Python311\python.exe"
IF EXIST "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python39\python.exe" SET PYTHON_CMD="C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python39\python.exe"
IF EXIST "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310\python.exe" SET PYTHON_CMD="C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310\python.exe"
IF EXIST "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe" SET PYTHON_CMD="C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe"

IF "%PYTHON_CMD%"=="" (
    echo Python not found in common locations.
    echo Please make sure Python is installed and try again.
    pause
    exit /b 1
)

echo Found Python at %PYTHON_CMD%
echo Starting server...

REM Start the Flask application
%PYTHON_CMD% app.py

echo.
echo If the browser doesn't open automatically, please go to:
echo http://localhost:5000
echo.
echo To stop the server, close this window.
pause 