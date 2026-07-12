#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "pyyaml",
# ]
# ///
"""
Convert Logseq page-property blocks into proper YAML frontmatter.

Logseq stores page metadata as the first block of a page, using
`key:: value` syntax, e.g.

    type:: article
    tags:: foo, bar
    date:: 2024-01-01
    - Actual content starts here...

This script pulls those `key:: value` lines out and turns them into a
YAML frontmatter block that pandoc (and static site generators like
Marmite, Jekyll, Hugo, Zola, etc.) can read.

Outline bullets are always flattened (one level stripped), and filenames
always have whitespace collapsed into underscores.

Usage:
    uv run logseq_to_frontmatter.py content --in-place
"""

import argparse
import re
from pathlib import Path
from typing import Optional

import yaml  # pip install pyyaml

PROP_RE = re.compile(r"^([A-Za-z][A-Za-z0-9_-]*)::\s*(.*)$")

# Keys whose values should become a YAML list when comma-separated
LIST_KEYS = {"tags", "aliases", "categories", "authors"}

# Logseq-internal keys that should never end up in the site's frontmatter
DROP_KEYS = {"id"}


def parse_properties(lines):
    """
    Consume leading `key:: value` lines, return (props, remaining_lines).
    Property lines may be indented (Logseq sometimes nests the page-property
    block under an implicit parent), so matching is done against the
    stripped line, not raw column position.
    """
    props = {}
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        m = PROP_RE.match(stripped)
        if not m:
            break
        key, value = m.group(1).strip(), m.group(2).strip()
        # Logseq page-refs look like [[Foo]] - strip the brackets
        value = re.sub(r"\[\[(.*?)\]\]", r"\1", value)
        if key.lower() in LIST_KEYS:
            # Always a list for these keys, even with a single value - e.g.
            # Marmite requires `tags` to be a list, not a bare string.
            props[key] = [v.strip() for v in value.split(",") if v.strip()]
        elif "," in value:
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
    Logseq's body is one big bulleted outline. Static site generators expect
    flat markdown, so this removes a single leading '- ' (and matching
    2-space indent) from every line, one level only. Deeper nesting is left
    intact so sub-bullets still render as lists.
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


def build_frontmatter(props: dict) -> str:
    if not props:
        return ""
    body = yaml.safe_dump(props, sort_keys=False, allow_unicode=True)
    return f"---\n{body}---\n\n"


def apply_public_convention(props: dict) -> None:
    """
    Logseq convention: `public:: false` marks a page as not-for-publishing.
    Marmite convention: `stream: draft` excludes a post from feeds/search/lists.

    - public:: false  -> drop `public`, add `stream: draft`
    - public:: true   -> drop `public` (nothing further needed, it's public by default)
    """
    for key in list(props.keys()):
        if key.lower() == "public":
            value = str(props.pop(key)).strip().lower()
            if value == "false":
                props["stream"] = "draft"


def detect_and_clean_frontmatter(lines):
    """
    Inspect a possible leading --- fence.

    Returns (is_real_frontmatter, cleaned_lines).

    A fence only counts as real, already-converted frontmatter if its
    content parses as a non-empty mapping AND none of its keys themselves
    end in a colon. That second check matters because Logseq's
    `id:: some-uuid` syntax is, unfortunately, ALSO valid YAML - it parses
    as {'id:': 'some-uuid'} - so a stray/broken '---'-wrapped Logseq
    property would otherwise be mistaken for genuine frontmatter and
    silently skipped forever.

    If a fence is found but doesn't look real, the fence markers are
    stripped (contents kept in place) so the enclosed lines can be
    re-parsed as normal Logseq properties instead of being lost.
    """
    i = 0
    while i < len(lines) and lines[i].strip() == "":
        i += 1
    if i >= len(lines):
        return False, lines

    if lines[i].strip() != "---":
        return False, lines

    for j in range(i + 1, len(lines)):
        if lines[j].strip() == "---":
            block = "".join(lines[i + 1 : j])
            try:
                parsed = yaml.safe_load(block)
            except Exception:
                parsed = None

            looks_real = (
                isinstance(parsed, dict)
                and len(parsed) > 0
                and not any(str(k).rstrip().endswith(":") for k in parsed.keys())
            )

            if looks_real:
                return True, lines

            # Stray/broken fence - strip the markers, keep enclosed content
            # so it gets a chance to be parsed as real Logseq properties.
            cleaned = lines[:i] + lines[i + 1 : j] + lines[j + 1 :]
            return False, cleaned

    return False, lines  # opening fence with no closing fence - leave as-is


def convert_file(path: Path, out_path: Path) -> bool:
    """Convert one file. Returns True if it was converted, False if skipped."""
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)

    is_real_frontmatter, lines = detect_and_clean_frontmatter(lines)
    if is_real_frontmatter:
        return False

    props, rest = parse_properties(lines)
    if not props:
        # No Logseq property block found - nothing to do.
        return False

    for key in list(props.keys()):
        if key.lower() in DROP_KEYS:
            del props[key]

    apply_public_convention(props)

    rest = strip_top_level_bullet(rest)

    new_text = build_frontmatter(props) + "".join(rest)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(new_text, encoding="utf-8")
    return True


def convert_path(src: Path, dest: Optional[Path] = None, recursive: bool = True) -> int:
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
        if convert_file(md_file, out_path):
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
    count = convert_path(args.src, dest=dest, recursive=not args.no_recursive)
    print(f"\nConverted {count} file(s).")


if __name__ == "__main__":
    main()
