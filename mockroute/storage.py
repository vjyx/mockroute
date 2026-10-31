from pathlib import Path
import json
import os

class StorageError(Exception):
     """Raised when Storage cannot read or write a file."""

class Storage:

    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)

    def init_workspace(self):
        self._create_if_missing("config.json")
        self._create_if_missing("data/users.json")

    def _create_if_missing(self, relative_path): #relative_path = folder/file_name
        """Create a JSON file containing {} unless it already exists."""
        path = self.base_dir / relative_path
        if not path.exists():
            self.write_json(relative_path, {})

    def write_json(self, relative_path, data):
        """Save data as JSON, safely, to a path inside base_dir.
        Raises StorageError if the data cannot be saved. """
        path = self.base_dir / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = path.with_name(path.name + ".tmp")
        try:
            with open(temp_path , "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            os.replace(temp_path, path)
        except (OSError, TypeError) as e:
            temp_path.unlink(missing_ok=True)
            raise StorageError(f"Cannot write {path}: {e}") from e

    def read_json(self, relative_path):
        """Load and return the JSON data at a path inside base_dir.
        Raises StorageError if the file is missing or contains invalid JSON."""
        path = self.base_dir / relative_path
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            raise StorageError(f"Cannot read {path}: {e}") from e
