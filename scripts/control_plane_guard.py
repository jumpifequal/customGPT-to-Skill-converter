#!/usr/bin/env python3
"""
Purpose: validate a generated control-plane map and behavioural-parity record for layered CustomGPT migrations.
When used: after human control-plane confirmation, after operational mirrors are generated, and before release.
Why it exists: source-byte preservation alone does not prove runtime executability, while transformed mirrors need provenance,
dependency, bootstrap-order, and parity evidence to avoid silent behavioural drift.
Inputs/parameters: target Skill directory containing references/control-plane-map.json and references/control-plane-parity.json.
Outputs: build-mode PASS diagnostics; exits 0 only when structural control-plane and parity requirements are complete.
High-level behaviour: validate artifact roles, canonical hashes/paths, runtime representation modes, dependency references,
bootstrap coverage/order, mirror requirements, and that every parity scenario has actually passed.
Failure semantics: never invents roles or results, never edits target files, and exits non-zero on missing, contradictory,
unresolved, failed, or not-run control-plane evidence.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROLES = {"PASSIVE_KB", "OPERATIONAL_CONTROL", "MIXED"}
MODES = {"PASSIVE_ONLY", "ORIGINAL_NATIVE", "DERIVED_MIRROR"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def load_json(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return payload


def validate_map(root: Path, payload: dict) -> list[str]:
    errors: list[str] = []
    strategy = payload.get("strategy")
    if strategy not in {"DUAL_RUNTIME_FIDELITY", "ORIGINAL_ONLY_RUNTIME_RISK", "CUSTOM_CONTROL_PLANE"}:
        errors.append("unsupported or missing control-plane strategy")

    artifacts = payload.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        return errors + ["control-plane map must contain a non-empty artifacts list"]

    source_paths: set[str] = set()
    operational_paths: list[str] = []

    for index, row in enumerate(artifacts):
        if not isinstance(row, dict):
            errors.append(f"artifact row {index} is not an object")
            continue
        source_path = row.get("source_path")
        role = row.get("artifact_role")
        canonical = row.get("canonical_target_path")
        canonical_hash = row.get("canonical_sha256")
        mode = row.get("runtime_representation_mode")
        runtime_target = row.get("runtime_target_path")
        native_confirmed = row.get("runtime_native_confirmed")

        if not isinstance(source_path, str) or not source_path:
            errors.append(f"artifact row {index} missing source_path")
            continue
        if source_path in source_paths:
            errors.append(f"duplicate source_path in control-plane map: {source_path}")
        source_paths.add(source_path)

        if role not in ROLES:
            errors.append(f"unsupported artifact_role for {source_path}: {role}")
        if mode not in MODES:
            errors.append(f"unsupported runtime_representation_mode for {source_path}: {mode}")

        if not isinstance(canonical, str) or not canonical:
            errors.append(f"missing canonical_target_path for {source_path}")
        else:
            canonical_file = root / canonical
            if not canonical_file.is_file():
                errors.append(f"canonical target missing for {source_path}: {canonical}")
        if not isinstance(canonical_hash, str) or not SHA256_RE.fullmatch(canonical_hash):
            errors.append(f"invalid canonical_sha256 for {source_path}")

        if role == "PASSIVE_KB" and mode not in {"PASSIVE_ONLY", "ORIGINAL_NATIVE", "DERIVED_MIRROR"}:
            errors.append(f"invalid passive KB mode for {source_path}")

        if role in {"OPERATIONAL_CONTROL", "MIXED"}:
            operational_paths.append(source_path)
            if strategy == "DUAL_RUNTIME_FIDELITY" and mode == "PASSIVE_ONLY":
                errors.append(f"operational artifact cannot be PASSIVE_ONLY under DUAL_RUNTIME_FIDELITY: {source_path}")
            if mode == "ORIGINAL_NATIVE" and native_confirmed is not True:
                errors.append(f"ORIGINAL_NATIVE requires runtime_native_confirmed=true: {source_path}")
            if mode == "DERIVED_MIRROR":
                if not isinstance(runtime_target, str) or not runtime_target:
                    errors.append(f"DERIVED_MIRROR missing runtime_target_path: {source_path}")
                elif not (root / runtime_target).is_file():
                    errors.append(f"runtime mirror missing for {source_path}: {runtime_target}")

        deps = row.get("depends_on", [])
        if not isinstance(deps, list) or not all(isinstance(item, str) for item in deps):
            errors.append(f"depends_on must be a string list for {source_path}")

    for row in artifacts:
        if not isinstance(row, dict):
            continue
        for dep in row.get("depends_on", []):
            if dep not in source_paths:
                errors.append(f"unknown dependency {dep} referenced by {row.get('source_path')}")

    bootstrap = payload.get("bootstrap_order")
    if operational_paths:
        if not isinstance(bootstrap, list) or not all(isinstance(item, str) for item in bootstrap):
            errors.append("bootstrap_order must be a string list when operational artifacts exist")
        else:
            if len(bootstrap) != len(set(bootstrap)):
                errors.append("bootstrap_order contains duplicates")
            missing = [item for item in operational_paths if item not in bootstrap]
            if missing:
                errors.append(f"bootstrap_order missing operational artifacts: {', '.join(missing)}")
            unknown = [item for item in bootstrap if item not in source_paths]
            if unknown:
                errors.append(f"bootstrap_order references unknown artifacts: {', '.join(unknown)}")

    if strategy == "ORIGINAL_ONLY_RUNTIME_RISK" and payload.get("runtime_risk_acknowledged") is not True:
        errors.append("ORIGINAL_ONLY_RUNTIME_RISK requires runtime_risk_acknowledged=true")

    return errors


def validate_parity(payload: dict) -> list[str]:
    errors: list[str] = []
    scenarios = payload.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        return ["control-plane parity record must contain at least one scenario"]
    ids: set[str] = set()
    required_categories = {"bootstrap"}
    seen_categories: set[str] = set()

    for index, row in enumerate(scenarios):
        if not isinstance(row, dict):
            errors.append(f"parity scenario {index} is not an object")
            continue
        scenario_id = row.get("id")
        category = row.get("category")
        status = row.get("status")
        if not isinstance(scenario_id, str) or not scenario_id:
            errors.append(f"parity scenario {index} missing id")
        elif scenario_id in ids:
            errors.append(f"duplicate parity scenario id: {scenario_id}")
        else:
            ids.add(scenario_id)
        if isinstance(category, str):
            seen_categories.add(category)
        if status not in {"PASS", "FAIL", "NOT_RUN"}:
            errors.append(f"invalid parity status for {scenario_id or index}: {status}")
        elif status != "PASS":
            errors.append(f"parity scenario not passed: {scenario_id or index}={status}")

    missing_categories = required_categories - seen_categories
    if missing_categories:
        errors.append(f"parity record missing required categories: {', '.join(sorted(missing_categories))}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("skill_dir")
    args = parser.parse_args()

    root = Path(args.skill_dir).resolve()
    map_path = root / "references" / "control-plane-map.json"
    parity_path = root / "references" / "control-plane-parity.json"
    errors: list[str] = []

    if not map_path.is_file():
        errors.append("references/control-plane-map.json is missing")
    if not parity_path.is_file():
        errors.append("references/control-plane-parity.json is missing")

    if not errors:
        try:
            errors.extend(validate_map(root, load_json(map_path)))
        except Exception as exc:
            errors.append(f"cannot validate control-plane map: {exc}")
        try:
            errors.extend(validate_parity(load_json(parity_path)))
        except Exception as exc:
            errors.append(f"cannot validate control-plane parity record: {exc}")

    if errors:
        print("CONTROL_PLANE_BLOCKED")
        for item in errors:
            print(f"- {item}")
        return 2

    print("CONTROL_PLANE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
