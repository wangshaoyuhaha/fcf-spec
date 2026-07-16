@echo off
setlocal
cd /d "%~dp0\..\.."
set "FCF_PYTHON="
if exist ".venv\Scripts\python.exe" set "FCF_PYTHON=.venv\Scripts\python.exe"
if not defined FCF_PYTHON set "FCF_PYTHON=python"
"%FCF_PYTHON%" -m apps.one_click_local_operations_app_1.cli status
pause
endlocal
