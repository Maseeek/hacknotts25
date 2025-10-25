@echo off
REM Setup script for AI Song Pipeline (Windows)
REM Creates a virtual environment and installs dependencies

echo Setting up AI Song Pipeline...
echo ================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    exit /b 1
)

echo Python version:
python --version

REM Create virtual environment
if exist "venv" (
    echo Virtual environment already exists at .\venv
    set /p RECREATE="Do you want to recreate it? (y/N): "
    if /i "%RECREATE%"=="y" (
        echo Removing existing virtual environment...
        rmdir /s /q venv
    ) else (
        echo Using existing virtual environment
    )
)

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo ✓ Virtual environment created at .\venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Verify pyvenv.cfg exists
if exist "venv\pyvenv.cfg" (
    echo ✓ pyvenv.cfg file created successfully
    echo   Location: venv\pyvenv.cfg
) else (
    echo Warning: pyvenv.cfg not found
)

REM Upgrade pip
echo Upgrading pip...
pip install --upgrade pip

REM Install dependencies
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt

echo.
echo ================================
echo Setup complete!
echo ================================
echo.
echo To activate the virtual environment, run:
echo   venv\Scripts\activate
echo.
echo To run the pipeline, use:
echo   python pipeline.py --song <path_to_song> --theme <theme>
echo.
echo Don't forget to set your OpenAI API key:
echo   set OPENAI_API_KEY=your-api-key-here
echo.

pause
