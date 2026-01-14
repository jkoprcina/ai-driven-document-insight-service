@echo off
REM Setup script for Document QA API (Windows)
REM This script automates the setup process

echo 🚀 Document QA API - Setup Script
echo ==================================
echo.

REM Check Python version
echo ✓ Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Python not found. Please install Python 3.11+
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set python_version=%%i
echo   Found Python %python_version%

REM Create virtual environment
echo.
echo ✓ Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo   Virtual environment created
) else (
    echo   Virtual environment already exists
)

REM Activate virtual environment
call venv\Scripts\activate.bat
echo   Virtual environment activated

REM Upgrade pip
echo.
echo ✓ Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1

REM Install dependencies
echo.
echo ✓ Installing Python dependencies...
pip install -r requirements.txt >nul 2>&1
echo   Dependencies installed

REM Download spaCy model
echo.
echo ✓ Downloading spaCy model...
python -m spacy download en_core_web_sm >nul 2>&1
echo   spaCy model downloaded

REM Create .env file
echo.
echo ✓ Creating environment configuration...
if not exist ".env" (
    copy .env.example .env
    echo   .env file created from template
    echo   ⚠️  Please edit .env to set SECRET_KEY and other settings
) else (
    echo   .env file already exists
)

REM Create necessary directories
echo.
echo ✓ Creating directories...
if not exist "logs" mkdir logs
if not exist "model_cache" mkdir model_cache
echo   Directories created

REM Validation
echo.
echo ✓ Validating setup...
python -c "import fastapi, pydantic, torch, transformers; print('  All imports OK')" >nul 2>&1
if errorlevel 1 (
    echo   ✗ Some imports failed. Try: pip install -r requirements.txt
    exit /b 1
)

echo.
echo ==================================
echo ✅ Setup complete!
echo ==================================
echo.
echo Next steps:
echo 1. Edit .env file: notepad .env
echo 2. Start the API: python main.py
echo 3. Open browser: http://localhost:8000/docs
echo.
echo For Streamlit UI:
echo   pip install streamlit
echo   streamlit run streamlit_app.py
echo.
echo Run tests:
echo   python test_integration.py
echo.
