@echo off
REM Patient Management System - Setup Script for Windows

echo ========================================
echo Patient Management System Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/5] Python found. Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/5] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo [4/5] Generating datasets...
cd model
python create_dataset.py
if errorlevel 1 (
    echo ERROR: Failed to create training dataset
    pause
    exit /b 1
)
cd ..

cd database
python create_hospital_data.py
if errorlevel 1 (
    echo ERROR: Failed to create hospital dataset
    pause
    exit /b 1
)
cd ..

echo [5/5] Training ML model... (This may take a minute)
cd model
python train_model.py
if errorlevel 1 (
    echo ERROR: Failed to train model
    pause
    exit /b 1
)
cd ..

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To start the application, run:
echo   python app.py
echo.
echo Then open your browser and go to:
echo   http://localhost:5000
echo.
echo Press any key to continue...
pause
