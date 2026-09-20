import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

from gui.main_window import launch

if __name__ == "__main__":
    sys.exit(launch())
