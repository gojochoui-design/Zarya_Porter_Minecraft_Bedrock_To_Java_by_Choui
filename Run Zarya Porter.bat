@echo off
title Zarya Porter by Choui
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python is not installed. Install Python 3.10 or newer from python.org first.
    pause
    exit /b 1
)
python "Zarya Porter.py"
if %errorlevel% neq 0 pause
