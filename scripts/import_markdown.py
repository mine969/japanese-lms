"""Compatibility wrapper for lesson packaging.

Use package_lessons.py for full beta LMS asset generation.
"""

from package_lessons import package


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    args = parser.parse_args()
    from pathlib import Path

    package(Path(args.source))


if __name__ == "__main__":
    main()
