"""
Purpose: validate a host-aware Conversation Session Lock integration.
When used: during build/packaging and optionally once when the calling skill is activated.
Why it exists: reject incomplete bindings, unsupported cross-turn persistence claims, and UX-transparency regressions deterministically.
Inputs/parameters: path to a SKILL.md-like integration file and --mode build|runtime.
Outputs: actionable developer diagnostics in build mode; no output on successful runtime validation.
High-level behaviour: parse the concrete Bind block, validate required fields and host-continuity semantics, then check required UX directives and prohibited persistence claims.
Failure semantics: never edits files, never infers missing values, exits non-zero on invalid configuration; runtime failures remain silent for internal handling.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

REQUIRED = (
    "SESSION_LOCK_ID",
    "ACTIVE_IDENTITY",
    "ACTIVATION_RULE",
    "EXIT_RULE",
    "PERSISTENT_INVARIANTS",
    "DRIFT_CRITERIA",
    "HOST_REINVOCATION_ASSUMPTION",
)

LIST_KEYS = {"PERSISTENT_INVARIANTS", "DRIFT_CRITERIA"}
HOST_VALUES = {"host-dependent", "host-guaranteed", "turn-scoped"}

HELP = {
    "SESSION_LOCK_ID": (
        "Identifies the internal latch unambiguously.",
        "Set a unique internal identifier.",
        "SESSION_LOCK_ID: REVIEWER_SESSION",
    ),
    "ACTIVE_IDENTITY": (
        "Defines the identity or operating mode protected against in-skill drift.",
        "Name the identity explicitly.",
        "ACTIVE_IDENTITY: Critical Reviewer",
    ),
    "ACTIVATION_RULE": (
        "Defines when the in-skill lock becomes active while the host has loaded the skill.",
        "State the activation event.",
        "ACTIVATION_RULE: direct invocation of this skill while loaded by the host",
    ),
    "EXIT_RULE": (
        "Defines when the in-skill identity may be released.",
        "Define explicit exit signals.",
        "EXIT_RULE: user explicitly asks to exit Critical Reviewer",
    ),
    "PERSISTENT_INVARIANTS": (
        "Defines behaviours that must remain stable while the skill is active.",
        "Provide at least one concrete invariant.",
        "PERSISTENT_INVARIANTS: [evidence-first review, preserve review rubric]",
    ),
    "DRIFT_CRITERIA": (
        "Makes in-skill degradation detectable before output.",
        "List observable drift signals.",
        "DRIFT_CRITERIA: [generic assistant behaviour, required state omitted]",
    ),
    "HOST_REINVOCATION_ASSUMPTION": (
        "Declares the trust boundary between the skill and the host runtime.",
        "Choose host-dependent, host-guaranteed, or turn-scoped.",
        "HOST_REINVOCATION_ASSUMPTION: host-dependent",
    ),
}

FORBIDDEN_CLAIMS = (
    r"guarantee(?:s|d)?\s+(?:that\s+)?(?:the\s+)?host\s+(?:will\s+)?(?:keep|retain|re-?invoke|load)",
    r"force(?:s|d)?\s+(?:the\s+)?host\s+to\s+(?:keep|retain|re-?invoke|load)",
    r"single invocation.{0,80}(?:always|universally|guarantee).{0,80}(?:later turns|across turns)",
    r"python.{0,80}(?:stores|holds|maintains).{0,80}(?:identity|persona|conversation state)",
)

def extract_bind(text: str) -> str:
    match = re.search(
        r"(?ms)^Bind:\s*\n(?P<body>.*?)(?=^Enforce\s+`?UX_TRANSPARENCY|^Apply the module|\Z)",
        text,
    )
    return match.group("body") if match else ""

def clean_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value.startswith("`") and value.endswith("`"):
        value = value[1:-1].strip()
    return value

def scalar_or_list(block: str, key: str) -> tuple[str | None, str]:
    match = re.search(
        rf"(?m)^\s*-\s*`?{re.escape(key)}`?\s*:\s*(?P<value>.*)$",
        block,
    )
    if not match:
        return "missing", ""

    value = clean_scalar(match.group("value"))

    if key in LIST_KEYS and not value:
        tail = block[match.end():]
        items: list[str] = []
        for line in tail.splitlines():
            if re.match(r"^\s{2,}-\s+\S", line):
                items.append(re.sub(r"^\s*-\s+", "", line).strip())
                continue
            if not line.strip():
                continue
            break
        if not items:
            return "empty", ""
        value = "\n".join(items)

    if not value:
        return "empty", ""

    if re.search(r"<[^>]+>", value):
        return "placeholder", value

    return None, value

def validate(text: str) -> list[tuple[str, str, str]]:
    errors: list[tuple[str, str, str]] = []
    block = extract_bind(text)

    if not block:
        return [("BIND_BLOCK", "missing", "Add a concrete Bind section.")]

    values: dict[str, str] = {}
    for key in REQUIRED:
        issue, value = scalar_or_list(block, key)
        if issue:
            errors.append((key, issue, ""))
        else:
            values[key] = value

    host_value = values.get("HOST_REINVOCATION_ASSUMPTION", "")
    if host_value and host_value not in HOST_VALUES:
        errors.append(
            (
                "HOST_REINVOCATION_ASSUMPTION",
                "unsupported",
                "Use exactly one of: host-dependent, host-guaranteed, turn-scoped.",
            )
        )

    if "UX_TRANSPARENCY = STRICT" not in text:
        errors.append(("UX_TRANSPARENCY", "missing", "Add UX_TRANSPARENCY = STRICT."))

    if not re.search(r"Apply the module silently", text, re.IGNORECASE):
        errors.append(("SILENT_APPLICATION", "missing", "Require silent application while the skill is active."))

    if not re.search(r"Never expose activation, persistence, drift detection, recovery, or deactivation", text, re.IGNORECASE):
        errors.append(("NO_ANNOUNCEMENT", "missing", "Forbid lock status and recovery narration."))

    for pattern in FORBIDDEN_CLAIMS:
        if re.search(pattern, text, re.IGNORECASE | re.DOTALL):
            errors.append(
                (
                    "HOST_PERSISTENCE_OVERCLAIM",
                    "contradictory",
                    "Remove claims that the skill or Python guard can force host-level cross-turn re-invocation.",
                )
            )
            break

    return errors

def print_build_errors(errors: list[tuple[str, str, str]]) -> None:
    print("CONFIGURATION_ERROR — Conversation Session Lock")
    print("Build status: BLOCKED")
    print()

    for index, (key, issue, custom_fix) in enumerate(errors, start=1):
        print(f"[{index}] Binding: {key}")
        print(f"Issue: {issue}")

        if key in HELP:
            why, fix, example = HELP[key]
            print(f"Why it matters: {why}")
            print(f"Fix: {fix}")
            print(f"Example: {example}")
        else:
            print("Why it matters: This control protects the host/skill trust boundary.")
            print(f"Fix: {custom_fix}")
            print("Example: declare cross-turn skill invocation as host-dependent unless the host explicitly guarantees it.")
        print()

    print("Next step: fix all items above, then re-run the build-time self-check.")

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("integration_file")
    parser.add_argument("--mode", choices=("build", "runtime"), default="build")
    args = parser.parse_args()

    path = Path(args.integration_file)
    errors = [("INPUT_FILE", "missing", f"Verify the file path: {path}")] if not path.is_file() else validate(path.read_text(encoding="utf-8"))

    if errors:
        if args.mode == "build":
            print_build_errors(errors)
        return 1

    if args.mode == "build":
        print("CONFIGURATION_OK — Conversation Session Lock")
        print("Build status: PASS")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
