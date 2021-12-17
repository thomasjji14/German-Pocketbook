import sys
import os

# CREDITS TO max OF Stackoverflow. necessary for pyinstaller
def getFile(relative_path):
    """ Get absolute path for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)