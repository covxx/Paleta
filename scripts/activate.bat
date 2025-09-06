@echo off
echo Activating Inventory Management System Virtual Environment...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found!
    echo Please run 'python -m venv venv' first to create it.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

echo.
echo Virtual environment activated!
echo Python: %where python%
echo Pip: %where pip%
echo.
echo To deactivate, run: deactivate
echo To install packages: pip install package_name
echo To run the app: python app.py
echo.

REM Keep the command prompt open
cmd /k
