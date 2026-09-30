@echo off
setlocal
cd /d "%~dp0"

set "PYTHON_CMD="
where py >nul 2>nul
if not errorlevel 1 (
    py -3 -c "import sys; assert sys.version_info >= (3, 10)" >nul 2>nul
    if not errorlevel 1 set "PYTHON_CMD=py -3"
)
if not defined PYTHON_CMD (
    where python >nul 2>nul
    if not errorlevel 1 (
        python -c "import sys; assert sys.version_info >= (3, 10)" >nul 2>nul
        if not errorlevel 1 set "PYTHON_CMD=python"
    )
)
if not defined PYTHON_CMD (
    echo Python 3.10 or newer was not found.
    echo Install Python from https://www.python.org/downloads/windows/
    echo Then reopen this file. Or use GitHub Codespaces as described in README.md.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Creating a local Python environment...
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 goto :failed
)

".venv\Scripts\python.exe" -c "import streamlit, pandas, matplotlib, requests" >nul 2>nul
if errorlevel 1 (
    echo Installing dependencies for the first run...
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 goto :failed
)

echo Opening the dashboard. Press Ctrl+C here to stop it.
".venv\Scripts\python.exe" -m streamlit run app.py
if errorlevel 1 goto :failed
exit /b 0

:failed
echo.
echo Startup failed. See the error above and the troubleshooting section in README.md.
pause
exit /b 1
