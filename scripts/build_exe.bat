@echo off
REM Build a single-file Windows executable using PyInstaller
REM Requires: Python 3.9+ on PATH

setlocal
pip install --upgrade pip >nul
pip install pyinstaller openpyxl >nul

REM If you prefer pandas for Excel reading, uncomment the next line (larger EXE)
REM pip install pandas >nul

pyinstaller --onefile --noconsole --name ReqIF-From-Excel src\reqif_app\excel_to_reqif.py

echo.
echo Build complete. Find the EXE in .\dist\ReqIF-From-Excel.exe
endlocal
