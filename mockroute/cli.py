import argparse
from pathlib import Path
import sys
from mockroute.storage import Storage, StorageError

def main(argv=None, base_dir=None):
    if base_dir is None:
        base_dir = Path.home() / ".config" / "mockroute"

    parser = argparse.ArgumentParser(prog="mockroute")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="create the workspace")
    add = sub.add_parser("add", help="register a route")
    add.add_argument("path")
    add.add_argument("--method", default="GET")
    sub.add_parser("list", help="show registered routes")

    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            storage = Storage(base_dir)
            storage.init_workspace()
            print(f"Workspace ready at {base_dir}")

        elif args.command == "add":
            storage = Storage(base_dir)
            storage.add_route(args.path, args.method)
            print(f"Added {args.method} {args.path}")

        elif args.command == "list":
            routes = Storage(base_dir).get_routes()
            if not routes:
                print("No routes registered")
            else:
                for route in routes:
                    print(f"{route['method']} {route['path']}")
    except StorageError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0
