@echo off
echo ================================================
echo   AMFI Mutual Fund Analyzer Pro - Quick Start
echo ================================================
echo.
echo This script will help you get started quickly.
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Python found. Checking dependencies...
echo.

REM Check if requirements are installed
pip show streamlit >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
) else (
    echo Dependencies already installed.
)

echo.
echo ================================================
echo   Starting AMFI Mutual Fund Analyzer Pro
echo ================================================
echo.
echo The application will open in your default browser.
echo To stop the application, press Ctrl+C in this window.
echo.

REM Start the main application
echo Starting AMFI Mutual Fund Analyzer...
streamlit run app.py

echo.
echo Application stopped.
pause
