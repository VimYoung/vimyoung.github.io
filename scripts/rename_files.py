#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# ///
"""
Recursively rename markdown files so their filenames have no whitespace
(runs of whitespace become a single underscore). Filename normalization
only - no content is touched.

Usage:
    uv run rename_files.py content
"""

import argparse
import re
from pathlib import Path


def sanitize_filename(name: str) -> str:
    """Replace any run of whitespace in a filename's stem with a single underscore."""
    p = Path(name)
    new_stem = re.sub(r'\s+', '_', p.stem.strip())
    return f"{new_stem}{p.suffix}"


def rename_single(path: Path) -> Path:
    """
    Rename one file if its name needs sanitizing.
    Returns the final path (new if renamed, unchanged otherwise).
    """
    sanitized_name = sanitize_filename(path.name)
    if sanitized_name == path.name:
        return path

    candidate = path.parent / sanitized_name
    if candidate.exists() and candidate != path:
        print(f"[warning] rename target already exists, skipping: {candidate}")
        return path

    path.rename(candidate)
    print(f"renamed: {path} -> {candidate}")
    return candidate


def rename_path(src: Path, recursive: bool = True) -> int:
    """
    Rename a single file or every .md file under a directory.
    Returns the number of files actually renamed.
    """
    pattern = "**/*.md" if recursive else "*.md"
    files = [src] if src.is_file() else sorted(src.glob(pattern))

    count = 0
    for path in files:
        final_path = rename_single(path)
        if final_path != path:
            count += 1
    return count


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", type=Path, help="Directory (or single file) to rename recursively")
    ap.add_argument("--no-recursive", action="store_true",
                     help="Only process the top-level directory, not subdirectories")
    args = ap.parse_args()

    count = rename_path(args.src, recursive=not args.no_recursive)
    print(f"\nRenamed {count} file(s).")


if __name__ == "__main__":
    main()
