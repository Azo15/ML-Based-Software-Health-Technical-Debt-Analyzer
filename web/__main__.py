"""Start the local API: python -m web --port 8765."""

import argparse

import uvicorn

from web.app import create_app


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--database", help="Optional SQLite database path")
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("Port must be between 1 and 65535")
    uvicorn.run(create_app(args.database), host="127.0.0.1", port=args.port, workers=1)


if __name__ == "__main__":
    main()
