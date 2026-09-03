#!/usr/bin/env python3
"""
Static CV generator.

Separates the CV content (data/cv_data.yaml) from its presentation
(templates/index.html.j2) and produces index.html at the repo root,
ready to be served by GitHub Pages.

Usage:
    python build.py
    python build.py --watch   # rebuild on every file change
    python build.py --check   # show a diff against the current
                               # index.html without overwriting it
"""
from __future__ import annotations

import argparse
import difflib
import sys
import time
import unicodedata
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "data" / "cv_data.yaml"
TEMPLATE_DIR = ROOT / "templates"
TEMPLATE_NAME = "index.html.j2"
OUTPUT_FILE = ROOT / "index.html"


# Encoding is explicit everywhere: we never fall back to the
# platform's default encoding (e.g. cp1252 on Windows), which is
# the most common cause of garbled characters.

def load_data(path: Path = DATA_FILE) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def render(data: dict) -> str:
    # autoescape is disabled: some fields intentionally contain a
    # bit of HTML (e.g. <br>, <span class="italic">) used to format
    # paragraphs.
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR, encoding="utf-8"),
        autoescape=select_autoescape(enabled_extensions=(), default=False),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template(TEMPLATE_NAME)
    html = template.render(**data)
    # Unicode normalization (NFC): guarantees a single binary
    # representation per accented character, even if the source
    # YAML was pasted from different tools (Word, macOS, etc.).
    return unicodedata.normalize("NFC", html)


def build(output: Path = OUTPUT_FILE) -> str:
    data = load_data()
    html = render(data)
    # newline="\n": force Unix line endings regardless of the OS
    # running the script, for a reproducible file in Git.
    with output.open("w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    rel = output.relative_to(ROOT)
    print(f"✓ {rel} generated ({len(html):,} characters, UTF-8)")
    return html


def check() -> int:
    """Render in memory and print a diff against the current index.html."""
    data = load_data()
    new_html = render(data)
    if OUTPUT_FILE.exists():
        with OUTPUT_FILE.open("r", encoding="utf-8") as f:
            old_html = f.read()
    else:
        old_html = ""
    diff = list(
        difflib.unified_diff(
            old_html.splitlines(keepends=True),
            new_html.splitlines(keepends=True),
            fromfile="index.html (current)",
            tofile="index.html (generated)",
        )
    )
    if not diff:
        print("✓ No difference: index.html is up to date.")
        return 0
    sys.stdout.writelines(diff)
    return 1


def watch() -> None:
    print("Watching data/ and templates/ (Ctrl+C to stop)...")
    watched = [DATA_FILE, TEMPLATE_DIR / TEMPLATE_NAME]
    last_mtimes = {p: p.stat().st_mtime for p in watched}
    build()
    try:
        while True:
            time.sleep(0.5)
            changed = False
            for p in watched:
                mtime = p.stat().st_mtime
                if mtime != last_mtimes[p]:
                    last_mtimes[p] = mtime
                    changed = True
            if changed:
                build()
    except KeyboardInterrupt:
        print("\nStopped.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--watch", action="store_true", help="rebuild on every change"
    )
    parser.add_argument(
        "--check", action="store_true", help="show diff without writing"
    )
    args = parser.parse_args()

    if args.check:
        sys.exit(check())
    elif args.watch:
        watch()
    else:
        build()


if __name__ == "__main__":
    main()