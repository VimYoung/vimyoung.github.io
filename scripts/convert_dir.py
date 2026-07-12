#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "pyyaml",
# ]
# ///
"""
Convenience runner: given a directory, first renames every .md file
recursively (whitespace -> underscore via rename_files.py), THEN converts
Logseq properties to YAML frontmatter recursively, in place
(via logseq_to_frontmatter.py). Rename pass always completes fully before
the conversion pass starts.

Must live in the same directory as rename_files.py and
logseq_to_frontmatter.py.

Usage:
    uv run convert_dir.py content
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rename_files import rename_path             # noqa: E402
from logseq_to_frontmatter import convert_path   # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("directory", type=Path, help="Directory to process, recursively, in place")
    args = ap.parse_args()

    if not args.directory.is_dir():
        raise SystemExit(f"Not a directory: {args.directory}")

    print("--- Renaming pass ---")
    renamed = rename_path(args.directory, recursive=True)
    print(f"Renamed {renamed} file(s).\n")

    print("--- Frontmatter conversion pass ---")
    converted = convert_path(args.directory, dest=None, recursive=True)
    print(f"Converted {converted} file(s) under {args.directory}")


if __name__ == "__main__":
    main()
