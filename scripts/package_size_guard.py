#!/usr/bin/env python3
"""
Purpose: calculate the projected compressed size of a Skill package before release.
When used: after target generation and before final packaging, and again after any size-reduction step.
Why it exists: the Skill upload limit is 25 MiB and raw directory size is not a reliable proxy for ZIP size.
Inputs/parameters: target Skill directory, optional --limit-mib, and optional --json output.
Outputs: projected compressed bytes, limit status, and a non-zero exit when the archive exceeds the configured limit.
High-level behaviour: create a temporary maximum-deflate ZIP using the same relative package layout, measure it,
then delete the temporary archive without modifying the target.
Failure semantics: exits non-zero for missing input, packaging errors, or limit exceedance; never alters source files.
"""

from __future__ import annotations

import argparse
import json
import tempfile
import zipfile
from pathlib import Path


def projected_zip_bytes(root: Path) -> int:
    with tempfile.TemporaryDirectory() as td:
        archive = Path(td) / "probe.zip"
        with zipfile.ZipFile(
            archive,
            "w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=9,
        ) as zf:
            for path in sorted(root.rglob("*")):
                if path.is_file():
                    arcname = (root.name / path.relative_to(root)).as_posix()
                    zf.write(path, arcname)
        return archive.stat().st_size


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("skill_dir")
    parser.add_argument("--limit-mib", type=float, default=25.0)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = Path(args.skill_dir).resolve()
    if not root.is_dir():
        print(f"ERROR: skill directory not found: {root}")
        return 2

    try:
        size = projected_zip_bytes(root)
    except Exception as exc:
        print(f"ERROR: cannot project package size: {exc}")
        return 2

    limit = int(args.limit_mib * 1024 * 1024)
    over = size > limit
    payload = {
        "projected_zip_bytes": size,
        "limit_bytes": limit,
        "over_limit": over,
        "recommended_next_step": "HUMAN_SIZE_GATE" if over else "PACKAGE",
    }

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"PROJECTED_ZIP_BYTES={size}")
        print(f"LIMIT_BYTES={limit}")
        print(f"STATUS={'OVER_LIMIT' if over else 'WITHIN_LIMIT'}")

    return 3 if over else 0


if __name__ == "__main__":
    raise SystemExit(main())
