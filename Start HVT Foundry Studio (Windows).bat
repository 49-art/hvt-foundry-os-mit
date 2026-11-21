@echo off
REM Double-click to start HVT Foundry Studio on Windows.
cd /d "%~dp0"
where py >nul 2>nul && (py -3 studio\app.py & goto end)
where python >nul 2>nul && (python studio\app.py & goto end)
echo Python 3 is not installed. Get it from https://www.python.org/downloads/ (tick "Add python.exe to PATH"), then try again.
:end
pause
