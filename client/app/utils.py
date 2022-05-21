import os.path
from pathlib import Path


def get_project_root() -> Path:
    return Path(__file__).parent.parent


def get_file_name(file_name):
    return os.path.join(get_project_root(), file_name)
