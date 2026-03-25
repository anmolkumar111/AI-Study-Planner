@echo off
REM ================================================================
REM AIStudyPlanner - Quick Setup Script for Windows
REM Run this file once to set up and start the project
REM Usage: Double-click this file OR run it from Command Prompt
REM ================================================================

echo.
echo  ╔══════════════════════════════════════════╗
echo  ║         AI Study Planner Setup           ║
echo  ║         Python Django Project            ║
echo  ╚══════════════════════════════════════════╝
echo.

REM Check if Python is installed
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please download Python from https://python.org and try again.
    pause
    exit /b 1
)

echo [1/5] Python found. Checking pip...
pip --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo [ERROR] pip not found. Please reinstall Python with pip.
    pause
    exit /b 1
)

echo [2/5] Creating virtual environment...
IF NOT EXIST "venv" (
    python -m venv venv
    echo Virtual environment created!
) ELSE (
    echo Virtual environment already exists, skipping.
)

echo [3/5] Activating virtual environment and installing Django...
call venv\Scripts\activate.bat
pip install -r requirements.txt --quiet
IF ERRORLEVEL 1 (
    echo [ERROR] Failed to install requirements.
    pause
    exit /b 1
)
echo Django installed successfully!

echo [4/5] Running database migrations...
python manage.py makemigrations planner
python manage.py migrate
echo Database ready!

echo [5/5] Creating default admin user (optional)...
echo You can skip this step and register through the website.
echo.

echo ================================================================
echo  Setup Complete! 
echo ================================================================
echo.
echo  To start the server, run:
echo     venv\Scripts\activate
echo     python manage.py runserver
echo.
echo  Then open your browser and go to:
echo     http://127.0.0.1:8000/
echo.
echo  To create a Django admin superuser:
echo     python manage.py createsuperuser
echo.

REM Ask if they want to start the server now
set /p START_SERVER="Start the development server now? (y/n): "
IF /I "%START_SERVER%"=="y" (
    echo.
    echo Starting server at http://127.0.0.1:8000/
    echo Press CTRL+C to stop the server.
    echo.
    python manage.py runserver
)

pause
