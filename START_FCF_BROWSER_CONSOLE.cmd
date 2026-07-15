@echo off
setlocal
cd /d "%~dp0"
python scripts\run_browser_product_console_runtime.py
if errorlevel 1 (
  echo.
  echo FCF Browser Product Console could not start.
  echo Review the guidance above, then try again.
  pause
)
endlocal
