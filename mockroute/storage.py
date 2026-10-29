from pathlib import Path

class Storage:

    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)

    def init_workspace(self):
        self.base_dir.mkdir(parents=True, exist_ok=True)
        p = self.base_dir / 'config.json'
        p.write_text('{}')
