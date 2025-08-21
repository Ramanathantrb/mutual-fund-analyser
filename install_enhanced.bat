@echo off
echo Installing Enhanced AMFI Mutual Fund Analyzer dependencies...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

echo Python found. Installing dependencies...
echo.

REM Upgrade pip first
python -m pip install --upgrade pip

REM Install core dependencies
echo Installing core dependencies...
pip install streamlit>=1.28.0
pip install plotly>=5.15.0
pip install pandas>=2.0.0
pip install numpy>=1.24.0
pip install requests>=2.31.0
pip install matplotlib>=3.7.0
pip install seaborn>=0.12.0
pip install scipy>=1.10.0
pip install urllib3>=2.0.0

REM Install enhanced features dependencies
echo.
echo Installing enhanced features...
pip install yfinance>=0.2.0
pip install ta>=0.10.0
pip install scikit-learn>=1.3.0
pip install streamlit-option-menu>=0.3.0

REM Optional advanced dependencies
echo.
echo Installing optional advanced features...
pip install streamlit-authenticator --quiet
pip install sqlite3 --quiet 2>nul || echo Note: sqlite3 is built-in with Python
pip install reportlab --quiet

echo.
echo =====================================================
echo ✅ Installation completed successfully!
echo =====================================================
echo.
echo To run the enhanced application:
echo   streamlit run enhanced_app.py
echo.
echo To run the original application:
echo   streamlit run app.py
echo.
echo For help and documentation, see ENHANCEMENT_GUIDE.md
echo.
pause
