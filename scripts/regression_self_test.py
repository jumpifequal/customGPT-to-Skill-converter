#!/usr/bin/env python3
"""
Purpose: Self-debug the CustomGPT-to-Skill converter and catch feature regressions before release.
When used: Run after any material feature evolution and immediately before packaging this converter Skill.
Why it exists: Converter features are coupled; a metadata or icon change can silently break package validity,
Knowledge preservation, or downstream validation.
Inputs/parameters: No user parameters; operates on this local Skill package and creates only temporary fixtures.
Outputs: PASS lines for every invariant and a final success marker; exits 0 only if the regression suite passes.
High-level behaviour: Check normative feature markers, validate the bundled UI assets and package, exercise inventory
hashing, run icon normalization on a synthetic raster fixture, and validate a synthetic generated Skill target.
Failure semantics: Any regression raises an assertion or subprocess error and exits non-zero; no failed release is valid.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"
VALIDATOR = ROOT / "scripts" / "validate_converted_skill.py"
INVENTORY = ROOT / "scripts" / "build_inventory.py"
ICON = ROOT / "scripts" / "icon_convert.py"
DETECTOR = ROOT / "scripts" / "detect_conversational_gpt.py"
LOCK_GUARD = ROOT / "scripts" / "conversation_lock_guard.py"
LOCK_REF = ROOT / "references" / "conversation_session_lock.md"
DETECTION_REF = ROOT / "references" / "conversational-gpt-detection.md"
KNOWLEDGE_REF = ROOT / "references" / "knowledge-migration.md"
KB_PRESERVE = ROOT / "scripts" / "kb_preserve.py"
DECISION_GUARD = ROOT / "scripts" / "decision_gate_guard.py"
SIZE_GUARD = ROOT / "scripts" / "package_size_guard.py"
CONTROL_GUARD = ROOT / "scripts" / "control_plane_guard.py"
CONTROL_REF = ROOT / "references" / "control-plane-migration.md"
HARNESS_REF = ROOT / "references" / "harness-templates.md"
HARNESS_SELECTOR = ROOT / "scripts" / "harness_profile_selector.py"
HUMAN_REF = ROOT / "references" / "human-control.md"
PARAMETER_RENDERER = ROOT / "scripts" / "render_parameter_report.py"
LEDGER = ROOT / "references" / "feature-regression.md"

FORBIDDEN = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".venv", "venv"}


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)
    print(f"PASS: {message}")


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )


def write_png_fixture(path: Path) -> None:
    try:
        from PIL import Image  # type: ignore
    except Exception as exc:
        raise RuntimeError(f"Pillow required for regression fixture: {exc}")
    image = Image.new("RGB", (320, 180), (90, 120, 150))
    image.save(path, format="PNG")


def main() -> None:
    text = SKILL.read_text(encoding="utf-8")
    ledger = LEDGER.read_text(encoding="utf-8")

    assert_true(text.startswith("---\n"), "SKILL.md has YAML frontmatter")
    assert_true(re.search(r"(?m)^name:\s*customgpt-to-skill\s*$", text) is not None, "skill name is stable")
    for marker in (
        "Mandatory full-skill read policy",
        "Anti-shortcut policy",
        "Icon normalization",
        "Coding discipline",
        "Self-debugging and evolutionary regression",
        "source-to-target manifest comparison",
        "Conversational classification and human gate",
        "Harness profiling and optional human gate",
    ):
        assert_true(marker in text, f"core feature marker retained: {marker}")
    for invariant in ("F001", "F004", "F005", "F007", "F012", "F013", "F014", "F015", "F016", "F017", "F018", "F019", "F020", "F021", "F022", "F023", "F024", "F025", "F026", "F027", "F028", "F029", "F030", "F031"):
        assert_true(invariant in ledger, f"regression invariant retained: {invariant}")

    knowledge_text = KNOWLEDGE_REF.read_text(encoding="utf-8")
    for choice in ("`PRESERVE_ORIGINAL_ONLY`", "`PRESERVE_PLUS_DERIVED`", "`CONVERT_AND_REPLACE`"):
        assert_true(choice in knowledge_text, f"DOCX gate explains option: {choice}")
    for choice in ("`LOSSLESS_FIRST`", "`EXTERNALIZE_WITH_REFERENCE`", "`LOSSY_WITH_APPROVAL`", "`ABORT`"):
        assert_true(choice in knowledge_text, f"size gate explains option: {choice}")
    assert_true("byte-for-byte" in knowledge_text, "Knowledge migration preserves authoritative originals")
    assert_true("non-authoritative" in knowledge_text, "derived DOCX mirrors are explicitly non-authoritative")

    control_text = CONTROL_REF.read_text(encoding="utf-8")
    for role in ("`PASSIVE_KB`", "`OPERATIONAL_CONTROL`", "`MIXED`"):
        assert_true(role in control_text, f"control-plane role documented: {role}")
    for strategy in ("`DUAL_RUNTIME_FIDELITY`", "`ORIGINAL_ONLY_RUNTIME_RISK`", "`CUSTOM_CONTROL_PLANE`"):
        assert_true(strategy in control_text, f"control-plane gate explains strategy: {strategy}")
    assert_true("bootstrap_order" in control_text, "control-plane policy preserves bootstrap order")
    assert_true("behavioural parity" in control_text.lower(), "control-plane policy requires behavioural parity")

    harness_text = HARNESS_REF.read_text(encoding="utf-8")
    for family in (
        "Classifier / Router Harness",
        "Extractor / Data Structuring Harness",
        "Research / Fact-Checking / RAG Harness",
        "Persistent / Conversational Agent Harness",
        "Workflow Automation / Tool-Using Harness",
        "Evaluator / Auditor Harness",
        "Coding Agent Harness",
        "Creative Generator Harness",
    ):
        assert_true(family in harness_text, f"harness template retained: {family}")
    for action in ("`ADD_RECOMMENDED`", "`NONE`", "`CUSTOM`"):
        assert_true(action in harness_text, f"harness human gate explains option: {action}")
    assert_true("Core Harness" in harness_text, "shared Core Harness retained")
    assert_true("Advisory only" in harness_text or "advisory" in harness_text.lower(), "harness selector remains advisory")

    human_text = HUMAN_REF.read_text(encoding="utf-8")
    for required in ("Decision Awareness Guide", "Conversion Parameter Report", "Why it matters", "Practical consequence", "CONFIRM ALL RECOMMENDED"):
        assert_true(required in human_text, f"Human-in-Control protocol retains: {required}")

    detection_text = DETECTION_REF.read_text(encoding="utf-8")
    for choice in (
        "`YES`", "`NO`", "`MIXED`",
        "`STRICT_LOCK`", "`BOUNDED_LOCK`", "`NO_LOCK`", "`CUSTOM`",
        "`host-dependent`", "`host-guaranteed`", "`turn-scoped`",
    ):
        assert_true(choice in detection_text, f"human gate explains option: {choice}")
    assert_true("### Choice guide" in detection_text, "human gate includes awareness rationale guide")
    assert_true("### Human reply format" in detection_text, "human gate preserves compact machine-readable reply")
    assert_true("practical consequence" in text or "practical consequence" in detection_text, "human gate requires consequence-aware approval")

    for path in ROOT.rglob("*"):
        assert_true(path.name not in FORBIDDEN, f"no forbidden residue: {path.name}")
        assert_true(path.suffix not in {".pyc", ".pyo"}, f"no bytecode residue: {path.name}")

    bundled = run(str(VALIDATOR), str(ROOT))
    assert_true("ALL TARGET VALIDATION CHECKS PASSED" in bundled.stdout, "converter package validates")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        source = temp / "source"
        source.mkdir()
        (source / "instructions.txt").write_text("Persistent behaviour", encoding="utf-8")
        (source / "knowledge.json").write_text('{"k":"v"}\n', encoding="utf-8")

        inv_path = temp / "inventory.json"
        run(str(INVENTORY), str(source), "--output", str(inv_path))
        payload = json.loads(inv_path.read_text(encoding="utf-8"))
        assert_true(payload["file_count"] == 2, "inventory captures all fixture files")
        assert_true(all(len(row["sha256"]) == 64 for row in payload["files"]), "inventory records SHA-256 hashes")


        # Byte-preserving Knowledge migration, including a DOCX-like binary fixture.
        kb_source = temp / "kb-source"
        kb_source.mkdir()
        (kb_source / "policy.docx").write_bytes(b"PK\x03\x04DOCX-BINARY-FIXTURE\x00\xff")
        (kb_source / "data.json").write_text('{"value": 7}\n', encoding="utf-8")
        kb_target = temp / "kb-target"
        (kb_target / "references").mkdir(parents=True)
        run(str(KB_PRESERVE), str(kb_source), str(kb_target))
        kb_manifest = json.loads((kb_target / "references" / "kb-manifest.json").read_text(encoding="utf-8"))
        assert_true(kb_manifest["file_count"] == 2, "KB preservation manifest records every source file")
        assert_true(
            (kb_target / "references" / "kb" / "original" / "policy.docx").read_bytes()
            == (kb_source / "policy.docx").read_bytes(),
            "DOCX original is preserved byte-for-byte",
        )

        # Human decision guard: valid fidelity choice passes; destructive conversion without acknowledgement fails.
        valid_decisions = temp / "decisions-valid.json"
        valid_decisions.write_text(json.dumps({
            "kb_preservation_mode": "BYTE_FOR_BYTE_PLUS_DERIVED",
            "decision_awareness_shown": True,
            "global_human_confirmed": True,
            "parameter_rows": [{
                "parameter": "Knowledge preservation mode",
                "selected_value": "BYTE_FOR_BYTE_ORIGINALS",
                "origin": "HUMAN",
                "rationale": "Preserve source evidence without silent normalization.",
                "practical_consequence": "Original Knowledge remains authoritative.",
            }],
            "control_plane_present": False,
            "control_plane_strategy": "NOT_APPLICABLE",
            "harness_source_present": False,
            "harness_candidate_present": False,
            "harness_action": "NOT_APPLICABLE",
            "harness_primary_family": "NOT_APPLICABLE",
            "harness_secondary_families": [],
            "docx_present": True,
            "docx_strategy": "PRESERVE_PLUS_DERIVED",
            "docx_human_confirmed": True,
            "semantic_loss_acknowledged": False,
            "conversational_classification": "NOT_APPLICABLE",
            "persona_drift": "NOT_APPLICABLE",
            "host_continuity": "NOT_APPLICABLE",
            "projected_zip_bytes": 1024,
            "oversize_strategy": "NOT_APPLICABLE",
        }), encoding="utf-8")
        gate_ok = run(str(DECISION_GUARD), str(valid_decisions), "--mode", "build")
        assert_true("DECISION_GATE_OK" in gate_ok.stdout, "deterministic DOCX decision record validates")

        invalid_decisions = temp / "decisions-invalid.json"
        invalid_decisions.write_text(json.dumps({
            "kb_preservation_mode": "BYTE_FOR_BYTE_ORIGINALS",
            "decision_awareness_shown": True,
            "global_human_confirmed": True,
            "parameter_rows": [{
                "parameter": "Knowledge preservation mode",
                "selected_value": "BYTE_FOR_BYTE_ORIGINALS",
                "origin": "HUMAN",
                "rationale": "Preserve source evidence without silent normalization.",
                "practical_consequence": "Original Knowledge remains authoritative.",
            }],
            "control_plane_present": False,
            "control_plane_strategy": "NOT_APPLICABLE",
            "harness_source_present": False,
            "harness_candidate_present": False,
            "harness_action": "NOT_APPLICABLE",
            "harness_primary_family": "NOT_APPLICABLE",
            "harness_secondary_families": [],
            "docx_present": True,
            "docx_strategy": "CONVERT_AND_REPLACE",
            "docx_human_confirmed": True,
            "semantic_loss_acknowledged": False,
            "conversational_classification": "NOT_APPLICABLE",
            "persona_drift": "NOT_APPLICABLE",
            "host_continuity": "NOT_APPLICABLE",
            "projected_zip_bytes": 1024,
            "oversize_strategy": "NOT_APPLICABLE",
        }), encoding="utf-8")
        invalid = subprocess.run(
            [sys.executable, str(DECISION_GUARD), str(invalid_decisions), "--mode", "build"],
            cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )
        assert_true(invalid.returncode != 0, "destructive DOCX conversion without semantic-loss acknowledgement is blocked")

        # Harness selector: advisory task-family profiling plus deterministic human gate.
        harness_source = temp / "harness-source.md"
        harness_source.write_text(
            "Use RAG retrieval over the knowledge base and authoritative source evidence to answer questions. "
            "Maintain a persistent persona across turns and follow-up conversation. Do not invent sources.",
            encoding="utf-8",
        )
        harness_profile = run(str(HARNESS_SELECTOR), str(harness_source))
        harness_payload = json.loads(harness_profile.stdout)
        assert_true(harness_payload["human_approval_required_for_new_harness"] is True, "harness selector never self-authorizes")
        assert_true(
            "RESEARCH_RAG" in harness_payload["recommendation"]
            or "PERSISTENT_CONVERSATIONAL" in harness_payload["recommendation"]
            or harness_payload["secondary_families"],
            "harness selector identifies source-backed task family",
        )

        harness_decisions = temp / "decisions-harness.json"
        harness_decisions.write_text(json.dumps({
            "kb_preservation_mode": "BYTE_FOR_BYTE_ORIGINALS",
            "decision_awareness_shown": True,
            "global_human_confirmed": True,
            "parameter_rows": [{
                "parameter": "Knowledge preservation mode",
                "selected_value": "BYTE_FOR_BYTE_ORIGINALS",
                "origin": "HUMAN",
                "rationale": "Preserve source evidence without silent normalization.",
                "practical_consequence": "Original Knowledge remains authoritative.",
            }],
            "control_plane_present": False,
            "control_plane_strategy": "NOT_APPLICABLE",
            "harness_source_present": False,
            "harness_candidate_present": True,
            "harness_action": "ADD_RECOMMENDED",
            "harness_primary_family": "RESEARCH_RAG",
            "harness_secondary_families": ["PERSISTENT_CONVERSATIONAL"],
            "harness_human_confirmed": True,
            "docx_present": False,
            "docx_strategy": None,
            "docx_human_confirmed": False,
            "semantic_loss_acknowledged": False,
            "conversational_classification": "NOT_APPLICABLE",
            "persona_drift": "NOT_APPLICABLE",
            "host_continuity": "NOT_APPLICABLE",
            "projected_zip_bytes": 1024,
            "oversize_strategy": "NOT_APPLICABLE",
        }), encoding="utf-8")
        harness_gate = run(str(DECISION_GUARD), str(harness_decisions), "--mode", "build")
        assert_true("DECISION_GATE_OK" in harness_gate.stdout, "human-approved harness decision validates")

        unapproved_harness = temp / "decisions-harness-unapproved.json"
        unapproved_harness.write_text(json.dumps({
            "kb_preservation_mode": "BYTE_FOR_BYTE_ORIGINALS",
            "decision_awareness_shown": True,
            "global_human_confirmed": True,
            "parameter_rows": [{
                "parameter": "Knowledge preservation mode",
                "selected_value": "BYTE_FOR_BYTE_ORIGINALS",
                "origin": "HUMAN",
                "rationale": "Preserve source evidence without silent normalization.",
                "practical_consequence": "Original Knowledge remains authoritative.",
            }],
            "control_plane_present": False,
            "control_plane_strategy": "NOT_APPLICABLE",
            "harness_source_present": False,
            "harness_candidate_present": True,
            "harness_action": "ADD_RECOMMENDED",
            "harness_primary_family": "RESEARCH_RAG",
            "harness_secondary_families": [],
            "harness_human_confirmed": False,
            "docx_present": False,
            "docx_strategy": None,
            "docx_human_confirmed": False,
            "semantic_loss_acknowledged": False,
            "conversational_classification": "NOT_APPLICABLE",
            "persona_drift": "NOT_APPLICABLE",
            "host_continuity": "NOT_APPLICABLE",
            "projected_zip_bytes": 1024,
            "oversize_strategy": "NOT_APPLICABLE",
        }), encoding="utf-8")
        unapproved = subprocess.run(
            [sys.executable, str(DECISION_GUARD), str(unapproved_harness), "--mode", "build"],
            cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )
        assert_true(unapproved.returncode != 0, "new harness insertion without human confirmation is blocked")

        # Human-in-Control parameter report must render deterministically from confirmed decisions.
        parameter_report = temp / "conversion-parameters.md"
        run(str(PARAMETER_RENDERER), str(valid_decisions), str(parameter_report))
        assert_true(parameter_report.is_file(), "conversion parameter report is generated")
        rendered = parameter_report.read_text(encoding="utf-8")
        assert_true("| Parameter | Selected value | Origin | Rationale | Practical consequence |" in rendered, "parameter report uses mandatory schema")
        report_check = run(str(PARAMETER_RENDERER), str(valid_decisions), str(parameter_report), "--check-existing")
        assert_true("PARAMETER_REPORT_OK" in report_check.stdout, "parameter report matches deterministic decision record")

        # Size guard must both pass a normal package and signal a deliberately tiny configured limit.
        size_ok = run(str(SIZE_GUARD), str(kb_target), "--json")
        size_payload = json.loads(size_ok.stdout)
        assert_true(size_payload["over_limit"] is False, "normal fixture package is within default size limit")
        size_over = subprocess.run(
            [sys.executable, str(SIZE_GUARD), str(kb_target), "--limit-mib", "0.000001", "--json"],
            cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )
        assert_true(size_over.returncode == 3, "oversize package condition triggers deterministic size gate")

        # Layered control-plane fixture: preserve canonical originals, native XML, derived DOCX mirror, bootstrap order, and parity.
        cp_target = temp / "control-plane-target"
        (cp_target / "references" / "kb" / "original").mkdir(parents=True)
        (cp_target / "references" / "runtime").mkdir(parents=True)
        canonical_l1 = cp_target / "references" / "kb" / "original" / "orchestrator.txt"
        canonical_l2 = cp_target / "references" / "kb" / "original" / "state-machine.xml"
        canonical_l3 = cp_target / "references" / "kb" / "original" / "meta-prompt.docx"
        mirror_l3 = cp_target / "references" / "runtime" / "meta-prompt.md"
        canonical_l1.write_text("bootstrap: state-machine -> meta-prompt", encoding="utf-8")
        canonical_l2.write_text("<router><state id='default'/></router>", encoding="utf-8")
        canonical_l3.write_bytes(b"PK\x03\x04CONTROL-DOCX")
        mirror_l3.write_text("# Operational mirror\nPersistent rules.", encoding="utf-8")

        import hashlib
        def fixture_hash(path):
            return hashlib.sha256(path.read_bytes()).hexdigest()

        cp_map = {
            "strategy": "DUAL_RUNTIME_FIDELITY",
            "runtime_risk_acknowledged": False,
            "bootstrap_order": ["orchestrator.txt", "state-machine.xml", "meta-prompt.docx"],
            "artifacts": [
                {
                    "source_path": "orchestrator.txt",
                    "artifact_role": "OPERATIONAL_CONTROL",
                    "canonical_target_path": "references/kb/original/orchestrator.txt",
                    "canonical_sha256": fixture_hash(canonical_l1),
                    "runtime_representation_mode": "ORIGINAL_NATIVE",
                    "runtime_target_path": "references/kb/original/orchestrator.txt",
                    "runtime_format": "text/plain",
                    "depends_on": ["state-machine.xml"],
                    "precedence_level": 1,
                    "runtime_native_confirmed": True,
                    "transformation_notes": "canonical original used directly",
                },
                {
                    "source_path": "state-machine.xml",
                    "artifact_role": "OPERATIONAL_CONTROL",
                    "canonical_target_path": "references/kb/original/state-machine.xml",
                    "canonical_sha256": fixture_hash(canonical_l2),
                    "runtime_representation_mode": "ORIGINAL_NATIVE",
                    "runtime_target_path": "references/kb/original/state-machine.xml",
                    "runtime_format": "application/xml",
                    "depends_on": ["meta-prompt.docx"],
                    "precedence_level": 2,
                    "runtime_native_confirmed": True,
                    "transformation_notes": "structured native control retained",
                },
                {
                    "source_path": "meta-prompt.docx",
                    "artifact_role": "MIXED",
                    "canonical_target_path": "references/kb/original/meta-prompt.docx",
                    "canonical_sha256": fixture_hash(canonical_l3),
                    "runtime_representation_mode": "DERIVED_MIRROR",
                    "runtime_target_path": "references/runtime/meta-prompt.md",
                    "runtime_format": "text/markdown",
                    "depends_on": [],
                    "precedence_level": 3,
                    "runtime_native_confirmed": False,
                    "transformation_notes": "canonical DOCX preserved; operational mirror generated",
                },
            ],
        }
        (cp_target / "references" / "control-plane-map.json").write_text(json.dumps(cp_map), encoding="utf-8")
        cp_parity = {
            "scenarios": [
                {"id": "bootstrap-order", "category": "bootstrap", "status": "PASS"},
                {"id": "routing-default", "category": "routing", "status": "PASS"},
                {"id": "precedence", "category": "precedence", "status": "PASS"},
            ]
        }
        (cp_target / "references" / "control-plane-parity.json").write_text(json.dumps(cp_parity), encoding="utf-8")
        cp_guard = run(str(CONTROL_GUARD), str(cp_target))
        assert_true("CONTROL_PLANE_OK" in cp_guard.stdout, "layered control-plane map and parity record validate")

        bad_map = dict(cp_map)
        bad_map["artifacts"] = [dict(item) for item in cp_map["artifacts"]]
        bad_map["artifacts"][2]["runtime_representation_mode"] = "PASSIVE_ONLY"
        (cp_target / "references" / "control-plane-map.json").write_text(json.dumps(bad_map), encoding="utf-8")
        bad_cp = subprocess.run(
            [sys.executable, str(CONTROL_GUARD), str(cp_target)],
            cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )
        assert_true(bad_cp.returncode != 0, "operational/mixed artifact cannot silently become passive-only")
        (cp_target / "references" / "control-plane-map.json").write_text(json.dumps(cp_map), encoding="utf-8")

        raster = temp / "source.png"
        write_png_fixture(raster)
        icon_out = temp / "icons"
        run(str(ICON), str(raster), str(icon_out))
        assert_true((icon_out / "icon.png").is_file(), "icon converter writes 64px PNG")
        from PIL import Image  # type: ignore
        with Image.open(icon_out / "icon.png") as rendered_icon:
            assert_true(rendered_icon.size == (64, 64), "icon.png is physically 64x64")
            rgba = rendered_icon.convert("RGBA")
            corner_alpha = [rgba.getpixel(point)[3] for point in ((0, 0), (63, 0), (0, 63), (63, 63))]
            assert_true(all(value > 0 for value in corner_alpha), "non-square raster is cover-reframed without transparent bands")
        assert_true((icon_out / "icon.svg").is_file(), "icon converter writes self-contained SVG")

        target = temp / "target-skill"
        (target / "agents").mkdir(parents=True)
        (target / "assets").mkdir()
        (target / "references").mkdir()
        (target / "scripts").mkdir()
        (target / "assets" / "icon.png").write_bytes((icon_out / "icon.png").read_bytes())
        (target / "assets" / "icon.svg").write_bytes((icon_out / "icon.svg").read_bytes())
        (target / "SKILL.md").write_text(
            "---\nname: fixture-skill\ndescription: Fixture converted skill used when testing regression validation.\n---\n"
            "# Fixture\n\n## Mandatory full-skill read policy\nRead all control resources before execution.\n",
            encoding="utf-8",
        )
        (target / "agents" / "openai.yaml").write_text(
            "interface:\n"
            "  display_name: Fixture Skill\n"
            "  short_description: Regression fixture.\n"
            "  icon_small: ./assets/icon.svg\n"
            "  icon_large: ./assets/icon.svg\n",
            encoding="utf-8",
        )
        target_check = run(str(VALIDATOR), str(target))
        assert_true("ALL TARGET VALIDATION CHECKS PASSED" in target_check.stdout, "representative generated target validates")
        # Clean-room contract: reject conversion residue in the released artifact.
        (target / "references" / "conversion-decisions.json").write_text("{}", encoding="utf-8")
        dirty = subprocess.run([sys.executable, str(VALIDATOR), str(target)], cwd=ROOT,
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        assert_true(dirty.returncode != 0 and "conversion residue" in dirty.stderr,
            "conversion decision record cannot ship in generated Skill")
        (target / "references" / "conversion-decisions.json").unlink()
        skill_file = target / "SKILL.md"
        original_skill = skill_file.read_text(encoding="utf-8")
        skill_file.write_text(original_skill + "\nConverted from a Custom GPT.\n", encoding="utf-8")
        dirty_wording = subprocess.run([sys.executable, str(VALIDATOR), str(target)], cwd=ROOT,
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        assert_true(dirty_wording.returncode != 0 and "conversion-history wording" in dirty_wording.stderr,
            "historical GPT claims cannot ship in generated Skill instructions")
        skill_file.write_text(original_skill, encoding="utf-8")
        clean_again = run(str(VALIDATOR), str(target))
        assert_true("ALL TARGET VALIDATION CHECKS PASSED" in clean_again.stdout,
            "clean operational instructions validate after residue removal")

        # Conversational candidate detector must flag explicit persistent persona semantics but never self-authorize.
        conversational_source = temp / "conversational.md"
        conversational_source.write_text(
            "You are ADRIANO. Maintain this persona across turns and follow-ups. "
            "Do not reset on topic changes. Exit the persona only when the user explicitly asks to disable it.",
            encoding="utf-8",
        )
        detection = run(str(DETECTOR), str(conversational_source))
        detected = json.loads(detection.stdout)
        assert_true(detected["classification"] == "CONVERSATIONAL_CANDIDATE", "detector flags explicit conversational persistence")
        assert_true(detected["human_confirmation_required"] is True, "conversational detection requires human confirmation")

        # Build a representative approved conversational target and validate its lock configuration.
        conv_target = temp / "conversation-target"
        (conv_target / "agents").mkdir(parents=True)
        (conv_target / "assets").mkdir()
        (conv_target / "references").mkdir()
        (conv_target / "scripts").mkdir()
        (conv_target / "assets" / "icon.png").write_bytes((icon_out / "icon.png").read_bytes())
        (conv_target / "assets" / "icon.svg").write_bytes((icon_out / "icon.svg").read_bytes())
        (conv_target / "references" / "conversation_session_lock.md").write_text(LOCK_REF.read_text(encoding="utf-8"), encoding="utf-8")
        (conv_target / "scripts" / "conversation_lock_guard.py").write_text(LOCK_GUARD.read_text(encoding="utf-8"), encoding="utf-8")
        (conv_target / "SKILL.md").write_text(
            "---\nname: conversation-fixture\ndescription: Conversational regression fixture used to validate approved persona-lock integration.\n---\n"
            "# Conversation Fixture\n\n"
            "## Mandatory full-skill read policy\nRead all control resources before execution.\n\n"
            "## Conversation Persistence Module\n\n"
            "Load and apply `references/conversation_session_lock.md`.\n\n"
            "Bind:\n"
            "- `SESSION_LOCK_ID`: `CONVERSATION_FIXTURE_SESSION`\n"
            "- `ACTIVE_IDENTITY`: `Conversation Fixture`\n"
            "- `ACTIVATION_RULE`: Conversation Fixture is invoked or loaded by the host for the current turn\n"
            "- `EXIT_RULE`: the user explicitly asks to exit or disable Conversation Fixture\n"
            "- `PERSISTENT_INVARIANTS`:\n"
            "  - preserve the approved conversational identity\n"
            "  - preserve the output contract\n"
            "- `DRIFT_CRITERIA`:\n"
            "  - generic assistant behaviour replaces the approved identity while active\n"
            "  - a topic change is treated as an in-skill reset\n"
            "- `HOST_REINVOCATION_ASSUMPTION`: `host-dependent`\n"
            "- `DISCLOSURE_RULE`: do not expose lock internals during normal operation\n\n"
            "Enforce `UX_TRANSPARENCY = STRICT`.\n"
            "Apply the module silently while the calling skill is active.\n"
            "Never expose activation, persistence, drift detection, recovery, or deactivation.\n"
            "Never claim that this module can force host re-invocation.\n",
            encoding="utf-8",
        )
        (conv_target / "agents" / "openai.yaml").write_text(
            "interface:\n"
            "  display_name: Conversation Fixture\n"
            "  short_description: Conversational regression fixture.\n"
            "  icon_small: ./assets/icon.svg\n"
            "  icon_large: ./assets/icon.svg\n",
            encoding="utf-8",
        )
        conv_check = run(str(VALIDATOR), str(conv_target))
        assert_true("ALL TARGET VALIDATION CHECKS PASSED" in conv_check.stdout, "approved conversational target validates")

        guard_check = run(str(LOCK_GUARD), str(conv_target / "SKILL.md"), "--mode", "build")
        assert_true("Build status: PASS" in guard_check.stdout, "conversation lock guard accepts complete bindings")

    print("ALL REGRESSION CHECKS PASSED")


if __name__ == "__main__":
    main()
