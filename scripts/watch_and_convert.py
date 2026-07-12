#!/usr/bin/env python3
"""
Watch a directory tree for new/changed .md files. On each event: rename
the file (whitespace -> underscore) first, then convert its content to
YAML frontmatter.

Usage:
    pip install watchdog pyyaml
    python watch_and_convert.py ./logseq/pages

Runs until you Ctrl+C.
"""

import argparse
import time
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from rename_files import rename_single, rename_path
from logseq_to_frontmatter import convert_file, convert_path


class MarkdownHandler(FileSystemEventHandler):
    def _maybe_convert(self, path_str):
        path = Path(path_str)
        if path.suffix != ".md" or not path.exists():
            return
        # Small delay so the editor/exporter finishes writing before we read.
        time.sleep(0.2)
        try:
            path = rename_single(path)          # rename pass first
            if convert_file(path, path):         # then conversion pass
                print(f"[converted] {path}")
        except Exception as e:
            print(f"[error] {path}: {e}")

    def on_created(self, event):
        if not event.is_directory:
            self._maybe_convert(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self._maybe_convert(event.src_path)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("directory", type=Path, help="Directory to watch recursively")
    args = ap.parse_args()

    # Process anything already sitting there before we start watching:
    # full rename pass, then full conversion pass.
    rename_path(args.directory, recursive=True)
    convert_path(args.directory, dest=None, recursive=True)

    handler = MarkdownHandler()
    observer = Observer()
    observer.schedule(handler, str(args.directory), recursive=True)
    observer.start()
    print(f"Watching {args.directory} for changes... (Ctrl+C to stop)")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
