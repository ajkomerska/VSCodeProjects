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


def archive_old_files(source_dir: Path = SOURCE_DIR, archive_dir: Path = ARCHIVE_DIR, days: int = ARCHIVE_AGE_DAYS) -> list[tuple[str, str]]:
    """Move files older than the cutoff age into the archive directory without reprocessing archived files."""
    archive_dir.mkdir(parents=True, exist_ok=True)

    cutoff_time = datetime.now() - timedelta(days=days)
    moved_files: list[tuple[str, str]] = []

    for file_path in sorted(source_dir.rglob("*")):
        if not file_path.is_file():
            continue

        if file_path.is_relative_to(archive_dir):
            continue

        if file_path.name == Path(__file__).name:
            continue

        last_modified = datetime.fromtimestamp(file_path.stat().st_mtime)
        if last_modified < cutoff_time:
            archive_path = archive_dir / file_path.name

            if archive_path.exists():
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                archive_path = archive_path.with_name(
                    f"{archive_path.stem}_{timestamp}{archive_path.suffix}"
                )

            shutil.move(str(file_path), str(archive_path))
            moved_files.append((file_path.name, archive_path.name))

    return moved_files


if __name__ == "__main__":
    print(f"Starting scanner. It will check every {SCAN_INTERVAL_SECONDS} seconds.")

    while True:
        print(f"\nScanning {SOURCE_DIR} for files older than {ARCHIVE_AGE_DAYS} days...")
        moved_files = archive_old_files()

        if moved_files:
            print("Moved the following files:")
            for original_name, archived_name in moved_files:
                print(f"- {original_name} -> {ARCHIVE_DIR.name}/{archived_name}")
        else:
            print("No files needed to be archived.")

        time.sleep(SCAN_INTERVAL_SECONDS)
