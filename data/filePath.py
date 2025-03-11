from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent
BASE_DIR = DATA_DIR.parent
ASSETS_DIR = BASE_DIR / "assets"

def assets_dir_func(fileName=""):
    return str(ASSETS_DIR / fileName)