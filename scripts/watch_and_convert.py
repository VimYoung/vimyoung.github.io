#!/usr/bin/env python3
"""
Watch a directory tree for new/changed .md files and convert Logseq
properties to YAML frontmatter in place, automatically, as soon as they
show up. Outline bullets are always flattened.

Usage:
    pip install watchdog pyyaml
    python watch_and_convert.py ./logseq/pages

Runs until you Ctrl+C. Good for: exporting from Logseq into a git repo
that's synced/committed separately, or just keeping a vault continuously
clean while you work.
"""

import argparse
import time
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from logseq_to_frontmatter import process_file, convert_path


class MarkdownHandler(FileSystemEventHandler):
    def _maybe_convert(self, path_str):
        path = Path(path_str)
        if path.suffix != ".md" or not path.exists():
            return
        # Small delay so the editor/exporter finishes writing before we read.
        time.sleep(0.2)
        try:
            result = process_file(path, path)
            if result["converted"]:
                print(f"[converted] {path}")
            if result["renamed_from"] is not None:
                print(f"[renamed] {result['renamed_from']} -> {result['final_path']}")
        except Exception as e:
            print(f"[error] {path}: {e}")

    def on_created(self, event):
        if not event.is_directory:
            self._maybe_convert(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self._maybe_convert(event.src_path)


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("directory", type=Path, help="Directory to watch recursively")
    args = ap.parse_args()

    # Convert anything already sitting there before we start watching.
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
