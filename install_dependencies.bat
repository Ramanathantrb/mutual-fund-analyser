@echo off
echo 📦 Installing AMFI Mutual Fund Analyzer Dependencies
echo.
echo 🔄 Installing required Python packages...
echo.

pip install streamlit>=1.28.0
pip install plotly>=5.15.0  
pip install pandas>=2.0.0
pip install numpy>=1.24.0
pip install requests>=2.31.0
pip install matplotlib>=3.7.0
pip install seaborn>=0.12.0
pip install scipy>=1.10.0
pip install urllib3>=2.0.0

echo.
echo ✅ Installation complete!
echo.
echo 🚀 You can now run:
echo    - run_web_app.bat (for web interface)
echo    - run_cli.bat (for command line)
echo.
pause
