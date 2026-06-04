"""Validate lesson metadata before LMS import."""

import argparse
import json
from pathlib import Path


REQUIRED_FIELDS = {"code", "status"}


def validate(metadata_path: Path) -> dict[str, object]:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    missing = sorted(REQUIRED_FIELDS - metadata.keys())
    return {
        "metadata_path": str(metadata_path),
        "valid": not missing,
        "missing_fields": missing,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("metadata", type=Path)
    args = parser.parse_args()
    print(json.dumps(validate(args.metadata), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

