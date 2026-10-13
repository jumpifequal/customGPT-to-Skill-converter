#!/usr/bin/env python3
"""
Purpose: produce an advisory harness-family recommendation from extracted CustomGPT instructions.
When used: after source-instruction extraction and before the optional human harness gate.
Why it exists: quickly map common CustomGPT operating patterns to reusable harness templates without letting heuristics
silently add behaviour that was absent from the source.
Inputs/parameters: one UTF-8 instruction file.
Outputs: JSON containing matched task families, a recommended primary family, optional secondary families, evidence signals,
and a mandatory note that human approval is required before adding a new harness.
High-level behaviour: scan source text for closed task-family signal patterns, rank matches by operational-risk priority,
and return HYBRID when multiple materially supported families are present.
Failure semantics: never edits source/target files, never inserts a harness, exits non-zero for missing/unreadable input,
and treats weak/no matches as CORE_ONLY rather than inventing a specialized family.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

FAMILIES = {
    "WORKFLOW_AUTOMATION": (
        1,
        [
            r"\b(api|tool call|connector|automation|workflow|scheduled|webhook|external action|write action|side effect)\b",
            r"\b(retry|idempotenc|approval|permission|rate limit)\b",
        ],
    ),
    "CODING_AGENT": (
        2,
        [
            r"\b(codebase|repository|repo|refactor|debug code|unit test|lint|typecheck|build)\b",
            r"\b(function|class|module|commit|patch|source code)\b",
        ],
    ),
    "EXTRACTOR_DATA": (
        3,
        [
            r"\b(extract|entity|entities|json|csv|schema|field|record|table|structured data)\b",
            r"\b(null|missing value|span fidelity|normalize|normalise)\b",
        ],
    ),
    "CLASSIFIER_ROUTER": (
        4,
        [
            r"\b(classif|label|route|routing|triage|score|category|intent|state machine|dispatcher)\b",
            r"\b(allowed labels|uncertain|out[_ -]?of[_ -]?scope)\b",
        ],
    ),
    "RESEARCH_RAG": (
        5,
        [
            r"\b(rag|retriev|research|fact[- ]?check|source|citation|knowledge base|document search|web search)\b",
            r"\b(evidence|verified|authoritative|primary source|insufficient context)\b",
        ],
    ),
    "EVALUATOR_AUDITOR": (
        6,
        [
            r"\b(audit|evaluate|review|rubric|grade|score|critique|validate)\b",
            r"\b(criterion|criteria|insufficient evidence|verdict)\b",
        ],
    ),
    "PERSISTENT_CONVERSATIONAL": (
        7,
        [
            r"\b(across turns|follow[- ]?up|conversation|session|persistent|persona|identity|assistant behaviour|system prompt)\b",
            r"\b(exit rule|deactivate|drift|maintain.*persona|remain.*identity)\b",
        ],
    ),
    "CREATIVE_GENERATOR": (
        8,
        [
            r"\b(creative|copy|story|narrative|naming|ideation|visual prompt|style|tone|campaign|marketing copy)\b",
            r"\b(genre|audience|brand voice|forbidden elements)\b",
        ],
    ),
}


def score_family(text: str, patterns: list[str]) -> tuple[int, list[str]]:
    evidence: list[str] = []
    score = 0
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE | re.DOTALL):
            score += 1
            evidence.append(pattern)
    return score, evidence


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("instruction_file")
    args = parser.parse_args()

    path = Path(args.instruction_file)
    if not path.is_file():
        raise SystemExit(f"input file not found: {path}")

    text = path.read_text(encoding="utf-8", errors="replace")
    matches: list[dict[str, object]] = []

    for family, (priority, patterns) in FAMILIES.items():
        score, evidence = score_family(text, patterns)
        if score:
            matches.append({
                "family": family,
                "priority": priority,
                "score": score,
                "evidence_patterns": evidence,
            })

    matches.sort(key=lambda item: (-int(item["score"]), int(item["priority"])))

    strong = [item for item in matches if int(item["score"]) >= 2]
    if not strong:
        recommendation = "CORE_ONLY"
        secondaries: list[str] = []
    elif len(strong) == 1:
        recommendation = str(strong[0]["family"])
        secondaries = []
    else:
        risk_sorted = sorted(strong, key=lambda item: int(item["priority"]))
        recommendation = "HYBRID:" + str(risk_sorted[0]["family"])
        secondaries = [str(item["family"]) for item in risk_sorted[1:]]

    print(json.dumps({
        "recommendation": recommendation,
        "secondary_families": secondaries,
        "matches": matches,
        "human_approval_required_for_new_harness": True,
        "note": "Advisory only. Preserve existing source harnesses; never add a new harness without human confirmation.",
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
