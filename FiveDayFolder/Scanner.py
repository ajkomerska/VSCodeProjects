from __future__ import annotations
import time
from datetime import datetime, timedelta
from pathlib import Path


SOURCE_DIR = Path(r"S:\@5-Day Folder").resolve()
ARCHIVE_DIR = SOURCE_DIR / "@Archived"
# Any folder older than 5 days will be deleted. This can be adjusted as needed.
ARCHIVE_AGE_DAYS = 5
# Code runs every 60 seconds.
SCAN_INTERVAL_SECONDS = 60


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

        try:
            last_modified = datetime.fromtimestamp(file_path.stat().st_mtime)
            if last_modified < cutoff_time:
                file_path.unlink()
                deleted_files.append((file_path.name, file_path.as_posix()))
        except (PermissionError, FileNotFoundError, OSError) as exc:
            print(f"Skipped inaccessible file: {file_path} ({exc})")
            continue

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
