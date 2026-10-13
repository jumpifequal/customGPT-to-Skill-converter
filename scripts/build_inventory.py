#!/usr/bin/env python3
"""
Purpose: Build a deterministic recursive inventory for a Custom GPT source tree or a generated Skill tree.
When used: Run before conversion and again after generation to detect silent file loss or unexplained deltas.
Why it exists: Reliable GPT-to-Skill conversion requires byte-level evidence of which assets were seen and preserved.
Inputs/parameters: A root directory and optional output JSON path.
Outputs: JSON containing relative path, size, SHA-256, and media type for every regular file.
High-level behaviour: Walk the root without following symlinks, reject unsafe relative paths, hash files in bounded chunks,
classify media type conservatively, sort entries by path, and optionally write the result atomically.
Failure semantics: Missing roots, symlinks, unreadable files, or write failures produce a clear error and non-zero exit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
import sys
import tempfile
from pathlib import Path

CHUNK_SIZE = 1024 * 1024


def fail(message: str) -> "NoReturn":
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(2)


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            while True:
                chunk = handle.read(CHUNK_SIZE)
                if not chunk:
                    break
                digest.update(chunk)
    except OSError as exc:
        fail(f"cannot read {path}: {exc}")
    return digest.hexdigest()


def inventory(root: Path) -> dict:
    root = root.resolve()
    if not root.is_dir():
        fail(f"root is not a directory: {root}")
    entries = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            fail(f"symlinks are not allowed in inventories: {path}")
        if not path.is_file():
            continue
        try:
            rel = path.relative_to(root).as_posix()
        except ValueError:
            fail(f"path escaped root: {path}")
        media_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        entries.append(
            {
                "path": rel,
                "bytes": path.stat().st_size,
                "sha256": hash_file(path),
                "media_type": media_type,
            }
        )
    return {"root": root.name, "file_count": len(entries), "files": entries}


def atomic_write_json(path: Path, payload: dict) -> None:
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=path.parent) as handle:
            handle.write(data)
            temp_name = handle.name
        os.replace(temp_name, path)
    except OSError as exc:
        fail(f"cannot write inventory: {exc}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a deterministic file inventory.")
    parser.add_argument("root", help="Directory to inventory.")
    parser.add_argument("--output", help="Optional JSON output path.")
    args = parser.parse_args()

    payload = inventory(Path(args.root))
    if args.output:
        atomic_write_json(Path(args.output), payload)
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
