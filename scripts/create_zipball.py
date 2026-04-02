#!/usr/bin/env python3
"""Create a zipball of the Chatty project, excluding build/cache artifacts."""

import zipfile
from datetime import datetime
from pathlib import Path

EXCLUDE_DIRS = {".git", ".pytest_cache", ".ruff_cache", ".venv", "__pycache__"}

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def should_exclude(path: Path) -> bool:
    """Return True if any component of *path* is in the exclusion set."""
    return bool(EXCLUDE_DIRS & set(path.parts))


def create_zipball() -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    project_name = PROJECT_ROOT.name
    zip_name = f"{project_name}_{timestamp}.zip"
    zip_path = PROJECT_ROOT / zip_name

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in sorted(PROJECT_ROOT.rglob("*")):
            if file == zip_path:
                continue

            rel = file.relative_to(PROJECT_ROOT)

            if should_exclude(rel):
                continue

            if file.is_file():
                zf.write(file, rel)

    print(f"Created {zip_path}  ({zip_path.stat().st_size / 1024:.1f} KB)")
    return zip_path


if __name__ == "__main__":
    create_zipball()
