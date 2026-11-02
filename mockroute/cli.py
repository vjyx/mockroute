import argparse
from pathlib import Path
import sys
from mockroute.storage import Storage, StorageError

from mockroute.storage import Storage

def main(argv=None, base_dir=None):
    if base_dir is None:
        base_dir = Path.home() / ".config" / "mockroute"

    parser = argparse.ArgumentParser(prog="mockroute")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="create the workspace")

    args = parser.parse_args(argv)
    if args.command == "init":
        try:
            storage = Storage(base_dir)
            storage.init_workspace()
        except StorageError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        print(f"Workspace ready at {base_dir}")
    return 0
