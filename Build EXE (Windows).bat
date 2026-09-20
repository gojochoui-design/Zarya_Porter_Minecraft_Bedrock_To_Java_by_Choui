@echo off
cd /d "%~dp0"
echo ============================================
echo   Zarya Porter by Choui - EXE builder
echo ============================================
python -m pip install --upgrade pyinstaller pillow pyside6
python tools\build_exe.py
echo.
echo The EXE is inside the "dist" folder.
pause
