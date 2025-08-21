@echo off
echo Starting Enhanced AMFI Mutual Fund Analyzer...
echo.

REM Check if dependencies are installed
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo ERROR: Dependencies not found!
    echo Please run install_enhanced.bat first
    echo.
    pause
    exit /b 1
)

echo Opening enhanced multi-page application...
echo.
echo Features available:
echo - 🔍 Fund Analyzer
echo - 📊 Fund Comparison
echo - 💰 SIP Calculator
echo - 📈 Portfolio Tracker
echo - 🎯 Goal Planner
echo.
echo Your browser will open automatically...
echo Press Ctrl+C to stop the application
echo.

streamlit run app.py
