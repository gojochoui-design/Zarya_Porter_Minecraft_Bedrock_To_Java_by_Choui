import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(ROOT, "Zarya Porter.py")
ICON = os.path.join(ROOT, "icon.ico")
ASSETS = os.path.join(ROOT, "assets")


def main():
    sep = ";" if os.name == "nt" else ":"
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm", "--clean",
        "--onefile", "--windowed",
        "--name", "Zarya Porter",
        "--add-data", ASSETS + sep + "assets",
    ]
    if os.name == "nt" and os.path.isfile(ICON):
        cmd += ["--icon", ICON]
    cmd.append(APP)
    print("Running PyInstaller...")
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode != 0:
        print("Build failed")
        sys.exit(result.returncode)
    ext = ".exe" if os.name == "nt" else ""
    print("Done: dist/Zarya Porter" + ext)


if __name__ == "__main__":
    main()
