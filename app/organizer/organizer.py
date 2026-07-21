import re
import shutil
from pathlib import Path


class FileOrganizer:

    def __init__(self):
        pass

    # ==========================================
    # Create Folder Structure
    # ==========================================

    def create_folder(self, destination, folder_names):

        current = Path(destination)

        for folder in folder_names:

            if folder is None:
                continue

            folder = str(folder).strip()

            if folder == "":
                continue

            # Avoid invalid Windows names and accidental path traversal from an
            # Excel value while retaining a readable folder name.
            folder = re.sub(r'[<>:"/\\|?*]+', "_", folder).strip(". ")
            if not folder or folder in {".", ".."}:
                continue

            current = current / folder

            current.mkdir(parents=True, exist_ok=True)

        return str(current)

    # ==========================================
    # Copy File
    # ==========================================

    def copy_file(self, source_file, destination_folder):

        return self._transfer(source_file, destination_folder, shutil.copy2)

    # ==========================================
    # Move File
    # ==========================================

    def move_file(self, source_file, destination_folder):

        return self._transfer(source_file, destination_folder, shutil.move)

    def _transfer(self, source_file, destination_folder, operation):
        """Transfer a file without overwriting an existing destination file."""
        source = Path(source_file)
        destination = Path(destination_folder)
        target = destination / source.name
        number = 1
        while target.exists():
            target = destination / f"{source.stem} ({number}){source.suffix}"
            number += 1
        operation(str(source), str(target))
        return str(target)
