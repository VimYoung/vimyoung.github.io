#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "pyyaml",
# ]
# ///
"""
Convenience runner: converts every .md file under a directory, recursively,
in place, using the conversion logic in logseq_to_frontmatter.py.

Must live in the same directory as logseq_to_frontmatter.py.

Usage:
    uv run convert_dir.py content
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from logseq_to_frontmatter import convert_path  # noqa: E402


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "directory", type=Path, help="Directory to convert, recursively, in place"
    )
    args = ap.parse_args()

    if not args.directory.is_dir():
        raise SystemExit(f"Not a directory: {args.directory}")

    count = convert_path(args.directory, dest=None, recursive=True)
    print(f"\nConverted {count} file(s) under {args.directory}")


if __name__ == "__main__":
    main()
