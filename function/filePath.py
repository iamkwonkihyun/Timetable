from pathlib import Path

FUNCTION_DIR = Path(__file__).resolve().parent
BASE_DIR = FUNCTION_DIR.parent
ASSETS_DIR = BASE_DIR / "assets"
DATA_DIR = BASE_DIR / "data"

def assets_dir_func(fileName=""):
    return str(ASSETS_DIR / fileName)

def data_dir_func(fileName=""):
    return str(DATA_DIR / fileName)