from __future__ import annotations
import shutil
import time
from datetime import datetime, timedelta
from pathlib import Path


SOURCE_DIR = Path(r"S:\@5-Day Folder").resolve()
ARCHIVE_DIR = SOURCE_DIR / "@Archived"
# Any folder older than 5 days will be moved to the archive folder. This can be adjusted as needed.
ARCHIVE_AGE_DAYS = 5
# Code runs every 60 seconds.
SCAN_INTERVAL_SECONDS = 60
MAX_ARCHIVE_FILENAME_STEM_LENGTH = 100


def _build_archive_path(archive_dir: Path, file_path: Path) -> Path:
    """Return a safe archive path, avoiding filename growth on repeated collisions."""
    archive_path = archive_dir / file_path.name
    if not archive_path.exists():
        return archive_path

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    suffix = file_path.suffix
    safe_stem = file_path.stem[:MAX_ARCHIVE_FILENAME_STEM_LENGTH].rstrip(". ")
    if not safe_stem:
        safe_stem = "archive"

    archive_path = archive_dir / f"{safe_stem}_{timestamp}{suffix}"
    counter = 1
    while archive_path.exists():
        archive_path = archive_dir / f"{safe_stem}_{timestamp}_{counter}{suffix}"
        counter += 1

    return archive_path


def archive_old_files(source_dir: Path = SOURCE_DIR, archive_dir: Path = ARCHIVE_DIR, days: int = ARCHIVE_AGE_DAYS) -> list[tuple[str, str]]:
    """Delete files older than the cutoff age, including any already archived files."""
    archive_dir.mkdir(parents=True, exist_ok=True)

    cutoff_time = datetime.now() - timedelta(days=days)
    deleted_files: list[tuple[str, str]] = []

    for file_path in sorted(source_dir.rglob("*")):
        if not file_path.is_file():
            continue

        if file_path.name == Path(__file__).name:
            continue

        last_modified = datetime.fromtimestamp(file_path.stat().st_mtime)
        if last_modified < cutoff_time:
            deleted_files.append((file_path.name, file_path.as_posix()))
            file_path.unlink()

    return deleted_files


if __name__ == "__main__":
    print(f"Starting scanner. It will check every {SCAN_INTERVAL_SECONDS} seconds.")

    while True:
        print(f"\nScanning {SOURCE_DIR} for files older than {ARCHIVE_AGE_DAYS} days...")
        deleted_files = archive_old_files()

        if deleted_files:
            print("Deleted the following files:")
            for original_name, deleted_path in deleted_files:
                print(f"- {original_name} -> {deleted_path}")
        else:
            print("No files needed to be deleted.")

        time.sleep(SCAN_INTERVAL_SECONDS)
