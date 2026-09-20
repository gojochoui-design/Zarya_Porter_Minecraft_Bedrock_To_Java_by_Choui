#!/bin/sh
cd "$(dirname "$0")"
echo "============================================"
echo "  Zarya Porter by Choui - binary builder"
echo "============================================"
python3 -m pip install --upgrade pyinstaller pillow pyside6
python3 tools/build_exe.py
echo
echo "The binary is inside the dist folder."
