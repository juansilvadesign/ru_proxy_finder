@echo off
echo.
echo ========================================
echo   RU Proxy Finder - Starting Program
echo ========================================
echo.

rem Set the script directory as the working directory
cd /d "%~dp0"

rem Check if virtual environment exists
if not exist ".env" (
    echo Installing virtualenv...
    pip install virtualenv
    if errorlevel 1 (
        echo Error: Failed to install virtualenv.
        pause
        exit /b 1
    )
    echo Creating virtual environment...
    virtualenv .env
    if errorlevel 1 (
        echo Error: Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo Virtual environment created successfully.
    echo.
)

rem Activate virtual environment
echo Activating virtual environment...
call .env\Scripts\activate
if errorlevel 1 (
    echo Error: Failed to activate virtual environment.
    pause
    exit /b 1
)

rem Install/update dependencies
echo Installing/updating dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo Error: Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Starting RU Proxy Finder...
echo ========================================
echo.

rem Run the main program
python main.py %*

rem Keep the window open if there was an error
if errorlevel 1 (
    echo.
    echo Program finished with errors.
    pause
) else (
    echo.
    echo Program completed successfully.
    echo Press any key to exit...
    pause >nul
)

rem Deactivate virtual environment
deactivate