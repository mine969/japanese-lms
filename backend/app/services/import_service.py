from pathlib import Path


def ensure_lesson_source_exists(path: Path) -> bool:
    return path.exists() and path.is_file()

