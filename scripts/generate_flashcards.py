"""Generate flashcard exports from approved flashcard source."""

import argparse
import json
from pathlib import Path


def generate(source: Path, output: Path) -> None:
    payload = {
        "source_path": str(source),
        "status": "pending_parser",
        "cards": [],
        "notes": "Add parser once flashcard source format is finalized.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    generate(args.source, args.output)


if __name__ == "__main__":
    main()

