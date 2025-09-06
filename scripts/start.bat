@echo off
echo Starting Inventory Management System...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found!
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Error creating virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo Installing required packages...
pip install -r requirements.txt

REM Start the application
echo Starting the application...
echo.
echo The system will be available at:
echo   - Local: http://localhost:5000
echo   - Network: http://[YOUR_IP]:5000
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py

pause
