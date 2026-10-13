#!/usr/bin/env python3
"""
Purpose: render and validate the mandatory user-facing Conversion Parameter Report from a deterministic decision record.
When used: after all applicable human choices are confirmed and before target Skill generation.
Why it exists: every migration must expose the parameters actually used, their origin, rationale, and practical consequence.
Inputs/parameters: path to conversion-decisions.json and output Markdown path.
Outputs: a Markdown parameter table plus validation status; exits 0 only when every report row is complete and origins are valid.
High-level behaviour: read the parameter_rows array, validate required fields and allowed origins, render one stable Markdown table,
and write it atomically to the requested output path.
Failure semantics: never invents rationale, consequence, or consent; exits non-zero on missing/incomplete/invalid rows and does not
silently create placeholder values.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path

ALLOWED_ORIGINS = {"HUMAN", "SOURCE", "DETECTED", "DERIVED"}
REQUIRED_FIELDS = ("parameter", "selected_value", "origin", "rationale", "practical_consequence")


def validate_rows(rows: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(rows, list) or not rows:
        return ["parameter_rows must be a non-empty list"]

    seen: set[str] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append(f"parameter row {index} must be an object")
            continue
        for field in REQUIRED_FIELDS:
            value = row.get(field)
            if value is None or str(value).strip() == "":
                errors.append(f"parameter row {index} missing {field}")
        parameter = str(row.get("parameter", "")).strip()
        if parameter:
            if parameter in seen:
                errors.append(f"duplicate parameter row: {parameter}")
            seen.add(parameter)
        origin = row.get("origin")
        if origin not in ALLOWED_ORIGINS:
            errors.append(f"invalid origin for {parameter or index}: {origin}")
    return errors


def escape_cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


def render(rows: list[dict[str, object]]) -> str:
    lines = [
        "# Conversion Parameter Report",
        "",
        "| Parameter | Selected value | Origin | Rationale | Practical consequence |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                escape_cell(row[field])
                for field in ("parameter", "selected_value", "origin", "rationale", "practical_consequence")
            )
            + " |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("decision_file")
    parser.add_argument("output_file")
    parser.add_argument("--check-existing", action="store_true")
    args = parser.parse_args()

    decision_path = Path(args.decision_file)
    output_path = Path(args.output_file)

    try:
        payload = json.loads(decision_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"PARAMETER_REPORT_BLOCKED: cannot read decision record: {exc}")
        return 2

    if not isinstance(payload, dict):
        print("PARAMETER_REPORT_BLOCKED: decision record must be a JSON object")
        return 2

    rows = payload.get("parameter_rows")
    errors = validate_rows(rows)
    if errors:
        print("PARAMETER_REPORT_BLOCKED")
        for error in errors:
            print(f"- {error}")
        return 2

    content = render(rows)

    if args.check_existing:
        if not output_path.is_file():
            print(f"PARAMETER_REPORT_BLOCKED: report not found: {output_path}")
            return 2
        existing = output_path.read_text(encoding="utf-8")
        if existing != content:
            print("PARAMETER_REPORT_BLOCKED: report does not match deterministic decision record")
            return 2
        print("PARAMETER_REPORT_OK")
        return 0

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=output_path.parent, delete=False, suffix=".tmp"
    ) as handle:
        handle.write(content)
        temp_name = handle.name
    os.replace(temp_name, output_path)

    print("PARAMETER_REPORT_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
