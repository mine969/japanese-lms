"""Convert approved lesson markdown into LMS JSON.

This script transforms structure only. It must not rewrite Japanese lesson content.
"""

import argparse
import json
from pathlib import Path


def import_markdown(source: Path, output: Path) -> None:
    text = source.read_text(encoding="utf-8")
    payload = {
        "source_path": str(source),
        "format": "markdown",
        "content": text,
        "import_notes": "Structure-only conversion; content unchanged.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    import_markdown(args.source, args.output)


if __name__ == "__main__":
    main()

