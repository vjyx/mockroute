from pathlib import Path

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
