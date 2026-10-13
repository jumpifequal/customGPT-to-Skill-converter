#!/usr/bin/env python3
"""
Purpose: deterministically validate human decisions required during CustomGPT-to-Skill conversion, including control-plane choices.
When used: after each human gate and again before target packaging.
Why it exists: global Human-in-Control approval plus control-plane, harness, conversational, DOCX-fidelity, Knowledge-preservation, and oversize-package choices must not be lost,
silently defaulted, or contradicted by later conversion steps.
Inputs/parameters: path to a JSON decision record and optional --mode build|runtime.
Outputs: developer-facing PASS/diagnostics in build mode; exits 0 only when all applicable gates are complete.
High-level behaviour: validate required decision fields conditionally from source facts and selected strategies.
Failure semantics: never edits the decision file, never invents missing choices, and exits non-zero on incomplete,
unsupported, or contradictory decisions.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

LIMIT_BYTES = 25 * 1024 * 1024

DOCX_STRATEGIES = {
    "PRESERVE_ORIGINAL_ONLY",
    "PRESERVE_PLUS_DERIVED",
    "CONVERT_AND_REPLACE",
}
CONVERSATIONAL = {"YES", "NO", "MIXED", "NOT_APPLICABLE"}
PERSONA = {"STRICT_LOCK", "BOUNDED_LOCK", "NO_LOCK", "CUSTOM", "NOT_APPLICABLE"}
HOST = {"host-dependent", "host-guaranteed", "turn-scoped", "NOT_APPLICABLE"}
OVERSIZE = {"LOSSLESS_FIRST", "EXTERNALIZE_WITH_REFERENCE", "LOSSY_WITH_APPROVAL", "ABORT", "NOT_APPLICABLE"}
CONTROL_PLANE = {"DUAL_RUNTIME_FIDELITY", "ORIGINAL_ONLY_RUNTIME_RISK", "CUSTOM_CONTROL_PLANE", "NOT_APPLICABLE"}
HARNESS_ACTIONS = {"PRESERVE_EXISTING", "ADD_RECOMMENDED", "NONE", "CUSTOM", "NOT_APPLICABLE"}
HARNESS_FAMILIES = {"CORE_ONLY", "CLASSIFIER_ROUTER", "EXTRACTOR_DATA", "RESEARCH_RAG", "PERSISTENT_CONVERSATIONAL", "WORKFLOW_AUTOMATION", "EVALUATOR_AUDITOR", "CODING_AGENT", "CREATIVE_GENERATOR", "HYBRID", "NOT_APPLICABLE"}
KB_MODES = {"BYTE_FOR_BYTE_ORIGINALS", "BYTE_FOR_BYTE_PLUS_DERIVED"}


def require(data: dict, key: str, errors: list[str]) -> object | None:
    value = data.get(key)
    if value is None or value == "":
        errors.append(f"missing required decision: {key}")
        return None
    return value


def validate(data: dict) -> list[str]:
    errors: list[str] = []

    if data.get("decision_awareness_shown") is not True:
        errors.append("decision_awareness_shown must be true for every conversion")
    if data.get("global_human_confirmed") is not True:
        errors.append("global_human_confirmed must be true for every conversion")

    parameter_rows = data.get("parameter_rows")
    if not isinstance(parameter_rows, list) or not parameter_rows:
        errors.append("parameter_rows must be a non-empty list for every conversion")
    else:
        allowed_origins = {"HUMAN", "SOURCE", "DETECTED", "DERIVED"}
        required_fields = ("parameter", "selected_value", "origin", "rationale", "practical_consequence")
        seen_parameters: set[str] = set()
        for index, row in enumerate(parameter_rows):
            if not isinstance(row, dict):
                errors.append(f"parameter row {index} must be an object")
                continue
            for field in required_fields:
                value = row.get(field)
                if value is None or str(value).strip() == "":
                    errors.append(f"parameter row {index} missing {field}")
            parameter_name = str(row.get("parameter", "")).strip()
            if parameter_name:
                if parameter_name in seen_parameters:
                    errors.append(f"duplicate parameter row: {parameter_name}")
                seen_parameters.add(parameter_name)
            if row.get("origin") not in allowed_origins:
                errors.append(f"invalid parameter origin for {parameter_name or index}: {row.get('origin')}")

    kb_mode = require(data, "kb_preservation_mode", errors)
    if kb_mode is not None and kb_mode not in KB_MODES:
        errors.append(f"unsupported kb_preservation_mode: {kb_mode}")

    control_plane_present = bool(require(data, "control_plane_present", errors))
    if control_plane_present:
        cp_strategy = require(data, "control_plane_strategy", errors)
        if cp_strategy is not None and cp_strategy not in CONTROL_PLANE - {"NOT_APPLICABLE"}:
            errors.append(f"unsupported control_plane_strategy: {cp_strategy}")
        if data.get("control_plane_human_confirmed") is not True:
            errors.append("control_plane_human_confirmed must be true when operational/mixed artifacts are present")
        if cp_strategy == "ORIGINAL_ONLY_RUNTIME_RISK" and data.get("runtime_risk_acknowledged") is not True:
            errors.append("runtime_risk_acknowledged must be true for ORIGINAL_ONLY_RUNTIME_RISK")
    elif data.get("control_plane_strategy") not in {None, "NOT_APPLICABLE"}:
        errors.append("control_plane_strategy should be NOT_APPLICABLE when no control plane is detected")

    harness_source_present = bool(require(data, "harness_source_present", errors))
    harness_candidate_present = bool(require(data, "harness_candidate_present", errors))
    harness_action = data.get("harness_action", "NOT_APPLICABLE")
    harness_family = data.get("harness_primary_family", "NOT_APPLICABLE")

    if harness_source_present:
        if harness_action != "PRESERVE_EXISTING":
            errors.append("harness_action must be PRESERVE_EXISTING when source harness controls are present")
        if harness_family not in HARNESS_FAMILIES - {"NOT_APPLICABLE"}:
            errors.append(f"unsupported harness_primary_family: {harness_family}")
    elif harness_candidate_present:
        if harness_action not in {"ADD_RECOMMENDED", "NONE", "CUSTOM"}:
            errors.append("harness_action must be ADD_RECOMMENDED, NONE, or CUSTOM when a new harness candidate is proposed")
        if data.get("harness_human_confirmed") is not True:
            errors.append("harness_human_confirmed must be true when a new harness candidate is proposed")
        if harness_action == "ADD_RECOMMENDED" and harness_family not in HARNESS_FAMILIES - {"NOT_APPLICABLE"}:
            errors.append("ADD_RECOMMENDED requires a supported harness_primary_family")
        if harness_action == "CUSTOM" and data.get("harness_custom_spec_complete") is not True:
            errors.append("harness_custom_spec_complete must be true for CUSTOM")
    else:
        if harness_action not in {None, "NOT_APPLICABLE"}:
            errors.append("harness_action should be NOT_APPLICABLE when no source harness or candidate is present")
        if harness_family not in {None, "NOT_APPLICABLE"}:
            errors.append("harness_primary_family should be NOT_APPLICABLE when no source harness or candidate is present")

    secondary = data.get("harness_secondary_families", [])
    if not isinstance(secondary, list) or not all(item in HARNESS_FAMILIES - {"HYBRID", "NOT_APPLICABLE"} for item in secondary):
        errors.append("harness_secondary_families must be a list of supported concrete harness families")

    docx_present = bool(require(data, "docx_present", errors))
    if docx_present:
        strategy = require(data, "docx_strategy", errors)
        if strategy is not None and strategy not in DOCX_STRATEGIES:
            errors.append(f"unsupported docx_strategy: {strategy}")
        if data.get("docx_human_confirmed") is not True:
            errors.append("docx_human_confirmed must be true when DOCX files are present")
        if strategy == "CONVERT_AND_REPLACE" and data.get("semantic_loss_acknowledged") is not True:
            errors.append("semantic_loss_acknowledged must be true for CONVERT_AND_REPLACE")

    classification = require(data, "conversational_classification", errors)
    if classification is not None and classification not in CONVERSATIONAL:
        errors.append(f"unsupported conversational_classification: {classification}")
    if classification in {"YES", "MIXED"}:
        persona = require(data, "persona_drift", errors)
        host = require(data, "host_continuity", errors)
        if persona is not None and persona not in PERSONA - {"NOT_APPLICABLE"}:
            errors.append(f"unsupported persona_drift: {persona}")
        if host is not None and host not in HOST - {"NOT_APPLICABLE"}:
            errors.append(f"unsupported host_continuity: {host}")
        if data.get("conversational_human_confirmed") is not True:
            errors.append("conversational_human_confirmed must be true for YES/MIXED")
    elif classification == "NO":
        if data.get("persona_drift") not in {None, "NOT_APPLICABLE"}:
            errors.append("persona_drift must be NOT_APPLICABLE when classification is NO")
        if data.get("host_continuity") not in {None, "NOT_APPLICABLE"}:
            errors.append("host_continuity must be NOT_APPLICABLE when classification is NO")

    projected = require(data, "projected_zip_bytes", errors)
    if isinstance(projected, bool) or (projected is not None and not isinstance(projected, int)):
        errors.append("projected_zip_bytes must be an integer")
    elif isinstance(projected, int):
        strategy = data.get("oversize_strategy", "NOT_APPLICABLE")
        if projected > LIMIT_BYTES:
            if strategy not in OVERSIZE - {"NOT_APPLICABLE"}:
                errors.append("oversize_strategy is required when projected_zip_bytes exceeds 25 MiB")
            if data.get("oversize_human_confirmed") is not True:
                errors.append("oversize_human_confirmed must be true when projected archive exceeds 25 MiB")
            if strategy == "LOSSY_WITH_APPROVAL" and data.get("lossy_change_authorized") is not True:
                errors.append("lossy_change_authorized must be true for LOSSY_WITH_APPROVAL")
        elif strategy not in {None, "NOT_APPLICABLE"}:
            errors.append("oversize_strategy should be NOT_APPLICABLE when projected archive is within limit")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("decision_file")
    parser.add_argument("--mode", choices=("build", "runtime"), default="build")
    args = parser.parse_args()

    path = Path(args.decision_file)
    if not path.is_file():
        errors = [f"decision file not found: {path}"]
    else:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                errors = ["decision record must be a JSON object"]
            else:
                errors = validate(payload)
        except Exception as exc:
            errors = [f"cannot read decision record: {exc}"]

    if errors:
        if args.mode == "build":
            print("DECISION_GATE_BLOCKED")
            for item in errors:
                print(f"- {item}")
        return 2

    if args.mode == "build":
        print("DECISION_GATE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
