#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "pyyaml",
#     "toml",
# ]
# ///
"""
Convert Logseq page-property blocks into proper YAML or TOML frontmatter.

Logseq stores page metadata as the first block of a page, using
`key:: value` syntax, e.g.

    type:: article
    tags:: foo, bar
    date:: 2024-01-01
    - Actual content starts here...

This script pulls those `key:: value` lines out and turns them into a
frontmatter block that pandoc (and static site generators like Jekyll,
Hugo, Zola, etc.) can read.

Usage:
    pip install pyyaml toml
    python logseq_to_frontmatter.py ./logseq/pages ./converted --format yaml --flatten

Then, optionally, normalize the markdown body with pandoc (it preserves
YAML frontmatter across markdown->markdown conversions):

    for f in converted/*.md; do
        pandoc "$f" -f markdown -t markdown --wrap=preserve -o "$f"
    done
"""

import argparse
import re
from pathlib import Path
from typing import Optional

import yaml  # pip install pyyaml

try:
    import toml  # pip install toml
except ImportError:
    toml = None

PROP_RE = re.compile(r"^([A-Za-z][A-Za-z0-9_-]*)::\s*(.*)$")

# Keys whose values should become a YAML/TOML list when comma-separated
LIST_KEYS = {"tags", "aliases", "categories", "authors"}


def parse_properties(lines):
    """Consume leading `key:: value` lines, return (props, remaining_lines)."""
    props = {}
    i = 0
    while i < len(lines):
        line = lines[i].rstrip("\n")
        m = PROP_RE.match(line)
        if not m:
            break
        key, value = m.group(1).strip(), m.group(2).strip()
        # Logseq page-refs look like [[Foo]] - strip the brackets
        value = re.sub(r"\[\[(.*?)\]\]", r"\1", value)
        if key.lower() in LIST_KEYS or "," in value:
            items = [v.strip() for v in value.split(",") if v.strip()]
            props[key] = items if len(items) > 1 else (items[0] if items else "")
        else:
            props[key] = value
        i += 1
    # Also skip a single blank line right after the property block, if present
    if i < len(lines) and lines[i].strip() == "":
        i += 1
    return props, lines[i:]


def strip_top_level_bullet(lines):
    """
    Logseq's body is one big bulleted outline. Many SSGs expect flat
    markdown, so this removes a single leading '- ' (and matching 2-space
    indent) from every line, one level only. Deeper nesting is left intact
    so sub-bullets still render as lists.
    """
    out = []
    for line in lines:
        if line.startswith("- "):
            out.append(line[2:])
        elif line.startswith("  ") and line.strip():
            out.append(line[2:])
        else:
            out.append(line)
    return out


def build_frontmatter(props, fmt):
    if not props:
        return ""
    if fmt == "yaml":
        body = yaml.safe_dump(props, sort_keys=False, allow_unicode=True)
        return f"---\n{body}---\n\n"
    else:  # toml
        if toml is None:
            raise SystemExit("TOML output requires: pip install toml")
        body = toml.dumps(props)
        return f"+++\n{body}+++\n\n"


def already_has_frontmatter(lines) -> bool:
    """Idempotency check: skip files that already start with --- or +++."""
    for line in lines:
        stripped = line.strip()
        if stripped == "":
            continue
        return stripped in ("---", "+++")
    return False


def convert_file(path: Path, out_path: Path, fmt: str, flatten: bool) -> bool:
    """Convert one file. Returns True if it was converted, False if skipped."""
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)

    if already_has_frontmatter(lines):
        return False

    props, rest = parse_properties(lines)
    if not props:
        # No Logseq property block found - nothing to do.
        return False

    if flatten:
        rest = strip_top_level_bullet(rest)

    new_text = build_frontmatter(props, fmt) + "".join(rest)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(new_text, encoding="utf-8")
    return True


def convert_path(
    src: Path,
    fmt: str,
    flatten: bool,
    dest: Optional[Path] = None,
    recursive: bool = True,
) -> int:
    """
    Convert a single file or every .md file under a directory.
    If dest is None, files are converted in place.
    """
    pattern = "**/*.md" if recursive else "*.md"
    files = [src] if src.is_file() else sorted(src.glob(pattern))

    count = 0
    for md_file in files:
        if dest is None:
            out_path = md_file
        else:
            rel = md_file.relative_to(src) if src.is_dir() else md_file.name
            out_path = dest / rel
        if convert_file(md_file, out_path, fmt, flatten):
            print(f"converted: {md_file}")
            count += 1
    return count


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "src", type=Path, help="Directory (or single file) of Logseq markdown"
    )
    ap.add_argument(
        "dest",
        type=Path,
        nargs="?",
        default=None,
        help="Output directory. Omit together with --in-place to edit in place.",
    )
    ap.add_argument(
        "--in-place",
        action="store_true",
        help="Write converted output back over the source files",
    )
    ap.add_argument(
        "--format",
        choices=["yaml", "toml"],
        default="yaml",
        help="Frontmatter format to emit (default: yaml)",
    )
    ap.add_argument(
        "--flatten",
        action="store_true",
        help="Strip one level of leading outline bullets from the body",
    )
    ap.add_argument(
        "--no-recursive",
        action="store_true",
        help="Only process the top-level directory, not subdirectories",
    )
    args = ap.parse_args()

    if not args.in_place and args.dest is None:
        raise SystemExit(
            "Provide a dest directory, or pass --in-place to edit files directly."
        )
    if args.in_place and args.dest is not None:
        raise SystemExit("Don't pass both a dest directory and --in-place.")

    dest = None if args.in_place else args.dest
    count = convert_path(
        args.src, args.format, args.flatten, dest=dest, recursive=not args.no_recursive
    )
    print(f"\nConverted {count} file(s).")


if __name__ == "__main__":
    main()
