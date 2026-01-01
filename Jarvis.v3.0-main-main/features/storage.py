import os

DATA_DIR_NAME = 'jarvis_data'

def get_data_dir():
    base = os.getcwd()
    data_dir = os.path.join(base, DATA_DIR_NAME)
    return data_dir

def ensure_data_dir():
    d = get_data_dir()
    try:
        os.makedirs(d, exist_ok=True)
    except Exception:
        pass
    return d

def data_path(filename: str) -> str:
    d = ensure_data_dir()
    return os.path.join(d, filename)

def migrate_existing(filenames):
    """Move existing files at repo root into the data directory if present."""
    d = ensure_data_dir()
    moved = []
    for fn in filenames:
        src = os.path.join(os.getcwd(), fn)
        dst = os.path.join(d, fn)
        try:
            if os.path.exists(src) and not os.path.exists(dst):
                os.replace(src, dst)
                moved.append((src, dst))
        except Exception:
            pass
    return moved
