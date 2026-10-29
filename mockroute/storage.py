from pathlib import Path
import json

class Storage:

    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)

    def init_workspace(self):
        self.base_dir.mkdir(parents=True, exist_ok=True)
        p = self.base_dir / 'config.json'
        if not p.exists():
            p.write_text('{}')

        data_folder = self.base_dir / "data"
        data_folder.mkdir(parents=True, exist_ok=True)
        u = data_folder / 'users.json'
        if not u.exists():
            u.write_text('{}')

    def write_json(self, relative_path, data):
        path = self.base_dir / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path , "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def read_json(self, relative_path):
        path = self.base_dir / relative_path
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
