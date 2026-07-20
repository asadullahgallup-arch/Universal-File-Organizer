from pathlib import Path
from collections import defaultdict
from app.config import FILE_TYPES


class FileIndexer:

    def __init__(self):
        self.file_index = defaultdict(list)

    def build_index(self, source_folder, file_type):

        self.file_index.clear()

        extensions = FILE_TYPES.get(file_type, [])

        source = Path(source_folder)

        if not source.exists():
            raise FileNotFoundError("Source folder does not exist.")

        extensions = {extension.lower() for extension in extensions}

        for file in source.rglob("*"):

            if not file.is_file():
                continue

            if extensions and file.suffix.lower() not in extensions:
                continue

            # Windows filenames are case-insensitive.  Indexing this way makes
            # Excel values such as "invoice-01" reliably match "Invoice-01.pdf".
            self.file_index[file.stem.casefold()].append(str(file))

        return self.file_index
