import os
from typing import List


def get_file_size(file: str) -> int:
    return os.path.getsize(file)


def get_files_size(files: List[str]) -> int:
    """return files total size in bytes
    """
    return sum([get_file_size(file) for file in files])


def remove_file(file: str) -> None:
    os.remove(file)
