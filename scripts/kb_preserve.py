#!/usr/bin/env python3
"""
Purpose: preserve a Custom GPT Knowledge Base byte-for-byte inside a generated Skill and build a verifiable manifest.
When used: after source inventory and human fidelity decisions, before target validation.
Why it exists: Knowledge migration must not silently normalize, rename, summarize, or drop source files.
Inputs/parameters: source KB directory, target Skill directory, and optional --source-prefix label.
Outputs: copied originals under references/kb/original/ plus references/kb-manifest.json with hashes and metadata.
High-level behaviour: recursively copy regular files without modifying bytes, retain relative paths, compute SHA-256,
record media type and size, and verify copied hashes before writing the manifest atomically.
Failure semantics: rejects symlinks and path escapes, stops on hash mismatch or copy failure, and never deletes sources.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
import shutil
import tempfile
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_dir")
    parser.add_argument("target_skill_dir")
    parser.add_argument("--source-prefix", default="knowledge")
    args = parser.parse_args()

    source = Path(args.source_dir).resolve()
    target = Path(args.target_skill_dir).resolve()
    if not source.is_dir() or not target.is_dir():
        print("ERROR: source_dir and target_skill_dir must both exist")
        return 2

    dest_root = target / "references" / "kb" / "original"
    dest_root.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []

    for src in sorted(source.rglob("*")):
        if src.is_symlink():
            print(f"ERROR: symlink not allowed in Knowledge source: {src}")
            return 2
        if not src.is_file():
            continue
        rel = src.relative_to(source)
        dst = dest_root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        src_hash = sha256(src)
        dst_hash = sha256(dst)
        if src_hash != dst_hash:
            print(f"ERROR: hash mismatch after copy: {rel}")
            return 2
        media_type, _ = mimetypes.guess_type(src.name)
        rows.append({
            "source_path": f"{args.source_prefix}/{rel.as_posix()}",
            "target_path": f"references/kb/original/{rel.as_posix()}",
            "bytes": src.stat().st_size,
            "sha256": src_hash,
            "media_type": media_type or "application/octet-stream",
            "authoritative": True,
            "derived_mirror": None,
        })

    manifest = {
        "preservation_mode": "BYTE_FOR_BYTE_ORIGINALS",
        "file_count": len(rows),
        "files": rows,
    }

    manifest_path = target / "references" / "kb-manifest.json"
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=manifest_path.parent, delete=False, suffix=".tmp"
    ) as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)
        handle.write("\n")
        temp_name = handle.name
    os.replace(temp_name, manifest_path)

    print(f"PRESERVED_FILES={len(rows)}")
    print(f"MANIFEST={manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
