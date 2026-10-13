#!/usr/bin/env python3
"""
Purpose: Validate the published repository layout and run the skill's own regression suite.
When used: Locally before a commit/release and in GitHub Actions on every push and pull request.
Why it exists: The repository wraps a skill package with documentation and governance files; those extras must not
break the skill package, and the skill's own self-tests must keep passing in a clean checkout.
Inputs/parameters: none; operates on the repository root (parent of this directory).
Outputs: PASS lines and a final success marker; exits 0 only when every check passes.
High-level behaviour: check required files, frontmatter, UI metadata paths, case-insensitive filename collisions,
relative Markdown links, then run scripts/regression_self_test.py and scripts/validate_converted_skill.py on the root.
Failure semantics: any failed assertion or non-zero subprocess exits non-zero; nothing is repaired automatically.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "SKILL.md",
    "agents/openai.yaml",
    "assets/icon.png",
    "assets/icon.svg",
    "CHANGELOG.md",
    "LICENSE",
    "README.md",
    "README.it.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "docs/architecture.md",
    "docs/decision-gates.md",
    "docs/runtime-tools.md",
    "docs/examples.md",
    "docs/migration-landscape.md",
    "docs/assets/logo.svg",
    "references/human-control.md",
    "references/feature-regression.md",
    "scripts/regression_self_test.py",
    "scripts/validate_converted_skill.py",
]

SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", "workspace", "tmp", "dist", "build"}


def ok(message: str) -> None:
    print(f"PASS: {message}")


def tracked_files() -> list[Path]:
    return [p for p in ROOT.rglob("*") if p.is_file() and not (set(p.relative_to(ROOT).parts) & SKIP_DIRS)]


def check_required() -> None:
    for rel in REQUIRED:
        assert (ROOT / rel).is_file(), f"missing required file: {rel}"
    ok("required files present")


def check_frontmatter() -> None:
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert match, "SKILL.md frontmatter missing"
    fm = yaml.safe_load(match.group(1))
    assert fm["name"] == "customgpt-to-skill", "SKILL.md name must be customgpt-to-skill"
    assert str(fm.get("description", "")).strip(), "SKILL.md description empty"
    ok("SKILL.md frontmatter")


def check_ui_metadata() -> None:
    ui = yaml.safe_load((ROOT / "agents/openai.yaml").read_text(encoding="utf-8"))
    for key in ("display_name", "short_description", "icon_small", "icon_large"):
        assert ui["interface"].get(key), f"agents/openai.yaml missing interface.{key}"
    for key in ("icon_small", "icon_large"):
        target = (ROOT / ui["interface"][key]).resolve()  # paths are relative to the skill root
        assert target.is_file(), f"agents/openai.yaml {key} does not resolve: {ui['interface'][key]}"
    ok("agent UI metadata and icon paths")


def check_case_collisions() -> None:
    seen: dict[str, Path] = {}
    for path in tracked_files():
        key = str(path.relative_to(ROOT)).lower()
        assert key not in seen, f"case-insensitive filename collision: {path} vs {seen[key]}"
        seen[key] = path
    ok("no case-insensitive filename collisions (Windows/macOS safe)")


def check_markdown_links() -> None:
    link = re.compile(r"\[[^\]]*\]\(([^)#\s]+)(?:#[^)]*)?\)")
    for md in [p for p in tracked_files() if p.suffix == ".md" and "references" not in p.parts and p.name != "SKILL.md"]:
        for target in link.findall(md.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            resolved = (md.parent / target).resolve()
            assert resolved.exists(), f"broken relative link in {md.relative_to(ROOT)}: {target}"
    ok("relative Markdown links resolve")


def run(cmd: list[str], marker: str) -> None:
    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    assert result.returncode == 0 and marker in result.stdout, f"failed: {' '.join(cmd)}"


def main() -> int:
    check_required()
    check_frontmatter()
    check_ui_metadata()
    check_case_collisions()
    check_markdown_links()
    run([sys.executable, "scripts/regression_self_test.py"], "ALL REGRESSION CHECKS PASSED")
    run([sys.executable, "scripts/validate_converted_skill.py", "."], "ALL TARGET VALIDATION CHECKS PASSED")
    print("REPOSITORY VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
