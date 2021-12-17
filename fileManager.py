import sys
import os

# CREDITS TO MAX OF Stackoverflow
# Source: https://stackoverflow.com/questions/7674790/bundling-data-files-with-pyinstaller-onefile
def getFile(relative_path) -> str:
    """ Get absolute path for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)