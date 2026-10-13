#!/usr/bin/env python3
"""
Purpose: Validate a generated Skill package after GPT-to-Skill conversion.
When used: Run after generation and before packaging or delivery.
Why it exists: Structural validity alone cannot detect missing Knowledge, broken icon references, dirty packages,
or coding-discipline regressions.
Inputs/parameters: Target Skill directory and optional source inventory JSON for preservation comparison.
Outputs: PASS lines plus a final validation summary; exits 0 only when every enforced invariant passes.
High-level behaviour: Validate frontmatter, required files, metadata paths, icon safety/dimensions, package hygiene,
Python helper headers, reference existence, and optional source-to-target preservation evidence.
Failure semantics: Every detected violation is reported; any violation exits non-zero and the package must not ship.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

FORBIDDEN_NAMES = {
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".coverage",
    ".venv", "venv", ".tox", ".nox", ".DS_Store"
}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo", ".swp", ".tmp", ".bak"}


def fail_all(errors: list[str]) -> "NoReturn":
    for error in errors:
        print(f"FAIL: {error}", file=sys.stderr)
    raise SystemExit(2)


def parse_frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        return {}
    data: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def png_size(path: Path) -> tuple[int, int] | None:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", data[16:24])


def check_svg(path: Path) -> list[str]:
    errors = []
    try:
        root = ET.fromstring(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"icon.svg is invalid XML: {exc}"]
    if root.tag.split("}", 1)[-1] != "svg":
        errors.append("icon.svg root is not svg")
    for elem in root.iter():
        name = elem.tag.split("}", 1)[-1]
        if name in {"script", "foreignObject"}:
            errors.append(f"icon.svg contains unsafe element {name}")
        for key, value in elem.attrib.items():
            lname = key.split("}", 1)[-1].lower()
            val = str(value).lower().strip()
            if lname.startswith("on"):
                errors.append(f"icon.svg contains event attribute {lname}")
            if lname == "href" and val.startswith(("http://", "https://", "javascript:")):
                errors.append("icon.svg contains external/executable href")
    return errors


def validate_helper_header(path: Path) -> list[str]:
    if path.name == "__init__.py":
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    head = "\n".join(text.splitlines()[:30]).lower()
    required = ["purpose:", "when used:", "why it exists:", "inputs/parameters:", "outputs:", "high-level behaviour:", "failure semantics:"]
    return [f"{path.relative_to(path.parents[1])} missing header field '{item}'" for item in required if item not in head]


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_kb_manifest(root: Path) -> list[str]:
    errors: list[str] = []
    manifest_path = root / "references" / "kb-manifest.json"
    if not manifest_path.is_file():
        return errors
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"cannot read references/kb-manifest.json: {exc}"]

    files = payload.get("files")
    if not isinstance(files, list):
        return ["references/kb-manifest.json 'files' must be a list"]

    for index, row in enumerate(files):
        if not isinstance(row, dict):
            errors.append(f"kb manifest row {index} is not an object")
            continue
        target_path = row.get("target_path")
        expected_hash = row.get("sha256")
        authoritative = row.get("authoritative")
        if not isinstance(target_path, str) or not target_path:
            errors.append(f"kb manifest row {index} missing target_path")
            continue
        path = root / target_path
        if not path.is_file():
            errors.append(f"kb manifest target missing: {target_path}")
            continue
        if authoritative is not True:
            errors.append(f"kb manifest original must be authoritative: {target_path}")
        if not isinstance(expected_hash, str) or len(expected_hash) != 64:
            errors.append(f"kb manifest hash invalid: {target_path}")
        elif file_sha256(path) != expected_hash:
            errors.append(f"kb manifest hash mismatch: {target_path}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a converted Skill.")
    parser.add_argument("skill_dir")
    parser.add_argument("--source-inventory", help="Optional source inventory JSON.")
    args = parser.parse_args()

    root = Path(args.skill_dir).resolve()
    errors: list[str] = []
    if not root.is_dir():
        fail_all([f"skill directory not found: {root}"])

    skill_md = root / "SKILL.md"
    agent_yaml = root / "agents" / "openai.yaml"
    icon_svg = root / "assets" / "icon.svg"
    icon_png = root / "assets" / "icon.png"

    for path in (skill_md, agent_yaml, icon_svg, icon_png):
        if not path.is_file():
            errors.append(f"required file missing: {path.relative_to(root)}")

    if skill_md.is_file():
        text = skill_md.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        name = fm.get("name", "")
        desc = fm.get("description", "")
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
            errors.append("frontmatter name must be lowercase hyphen-case")
        if not desc or len(desc) > 1024:
            errors.append("frontmatter description must be 1-1024 characters")
        if "Mandatory full-skill read" not in text and "Mandatory full-skill read policy" not in text:
            errors.append("mandatory full-skill-read policy is missing")

    if agent_yaml.is_file():
        yaml_text = agent_yaml.read_text(encoding="utf-8")
        for key in ("display_name:", "short_description:", "icon_small:", "icon_large:"):
            if key not in yaml_text:
                errors.append(f"agents/openai.yaml missing {key[:-1]}")
        for match in re.findall(r"icon_(?:small|large):\s*(\S+)", yaml_text):
            rel = match.strip().strip('"').strip("'")
            if rel.startswith("./"):
                rel = rel[2:]
            if not (root / rel).is_file():
                errors.append(f"broken icon path in agents/openai.yaml: {match}")

    if icon_svg.is_file():
        errors.extend(check_svg(icon_svg))
    if icon_png.is_file():
        size = png_size(icon_png)
        if size != (64, 64):
            errors.append(f"icon.png must be physically 64x64; got {size}")

    # Conversational targets that declare the session lock must ship and validate the full control plane.
    if skill_md.is_file():
        text = skill_md.read_text(encoding="utf-8")
        if "## Conversation Persistence Module" in text:
            lock_ref = root / "references" / "conversation_session_lock.md"
            lock_guard = root / "scripts" / "conversation_lock_guard.py"
            if not lock_ref.is_file():
                errors.append("conversation lock declared but references/conversation_session_lock.md is missing")
            if not lock_guard.is_file():
                errors.append("conversation lock declared but scripts/conversation_lock_guard.py is missing")
            if lock_guard.is_file():
                try:
                    result = subprocess.run(
                        [sys.executable, str(lock_guard), str(skill_md), "--mode", "build"],
                        cwd=root,
                        text=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        check=False,
                    )
                    if result.returncode != 0:
                        detail = (result.stdout or result.stderr).strip().replace("\n", " | ")
                        errors.append(f"conversation lock build validation failed: {detail}")
                except Exception as exc:
                    errors.append(f"conversation lock guard could not run: {exc}")

    for path in root.rglob("*"):
        if path.name in FORBIDDEN_NAMES:
            errors.append(f"forbidden package residue: {path.relative_to(root)}")
        if path.is_file() and path.suffix.lower() in FORBIDDEN_SUFFIXES:
            errors.append(f"forbidden package file: {path.relative_to(root)}")
        if path.is_symlink():
            errors.append(f"symlink not allowed in final package: {path.relative_to(root)}")

    scripts = root / "scripts"
    if scripts.is_dir():
        for path in scripts.glob("*.py"):
            errors.extend(validate_helper_header(path))

    errors.extend(validate_kb_manifest(root))

    control_map = root / "references" / "control-plane-map.json"
    control_parity = root / "references" / "control-plane-parity.json"
    control_guard = root / "scripts" / "control_plane_guard.py"
    if control_map.is_file() or control_parity.is_file():
        if not control_map.is_file() or not control_parity.is_file():
            errors.append("control-plane validation requires both control-plane-map.json and control-plane-parity.json")
        if not control_guard.is_file():
            errors.append("control-plane records exist but scripts/control_plane_guard.py is missing")
        elif control_map.is_file() and control_parity.is_file():
            try:
                result = subprocess.run(
                    [sys.executable, str(control_guard), str(root)],
                    cwd=root,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )
                if result.returncode != 0:
                    detail = (result.stdout or result.stderr).strip().replace("\n", " | ")
                    errors.append(f"control-plane validation failed: {detail}")
            except Exception as exc:
                errors.append(f"control-plane guard could not run: {exc}")

    decisions = root / "references" / "conversion-decisions.json"
    decision_guard = root / "scripts" / "decision_gate_guard.py"
    parameter_report = root / "references" / "conversion-parameters.md"
    parameter_renderer = root / "scripts" / "render_parameter_report.py"
    if decisions.is_file():
        if not decision_guard.is_file():
            errors.append("conversion-decisions.json exists but scripts/decision_gate_guard.py is missing")
        else:
            try:
                result = subprocess.run(
                    [sys.executable, str(decision_guard), str(decisions), "--mode", "build"],
                    cwd=root,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )
                if result.returncode != 0:
                    detail = (result.stdout or result.stderr).strip().replace("\n", " | ")
                    errors.append(f"conversion decision validation failed: {detail}")
            except Exception as exc:
                errors.append(f"decision gate guard could not run: {exc}")

        if not parameter_report.is_file():
            errors.append("conversion-decisions.json exists but references/conversion-parameters.md is missing")
        if not parameter_renderer.is_file():
            errors.append("conversion-decisions.json exists but scripts/render_parameter_report.py is missing")
        elif parameter_report.is_file():
            try:
                result = subprocess.run(
                    [sys.executable, str(parameter_renderer), str(decisions), str(parameter_report), "--check-existing"],
                    cwd=root,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )
                if result.returncode != 0:
                    detail = (result.stdout or result.stderr).strip().replace("\n", " | ")
                    errors.append(f"conversion parameter report validation failed: {detail}")
            except Exception as exc:
                errors.append(f"parameter report validator could not run: {exc}")

    if args.source_inventory:
        inv_path = Path(args.source_inventory)
        try:
            payload = json.loads(inv_path.read_text(encoding="utf-8"))
            source_files = payload.get("files", [])
            if not isinstance(source_files, list):
                errors.append("source inventory 'files' must be a list")
            # This validator cannot infer semantic mapping automatically. It enforces that a preservation report exists.
            report = root / "references" / "source-target-preservation.json"
            if source_files and not report.is_file():
                errors.append("source inventory supplied but references/source-target-preservation.json is missing")
        except Exception as exc:
            errors.append(f"cannot read source inventory: {exc}")

    if errors:
        fail_all(errors)
    print("PASS: structural validation")
    print("PASS: metadata and icon references")
    print("PASS: icon safety and dimensions")
    print("PASS: package hygiene")
    print("PASS: Python helper header discipline")
    print("PASS: Knowledge manifest integrity when present")
    print("PASS: deterministic conversion decisions when present")
    print("PASS: Human-in-Control parameter report when decisions are present")
    print("PASS: control-plane map/parity integrity when present")
    print("ALL TARGET VALIDATION CHECKS PASSED")


if __name__ == "__main__":
    main()
