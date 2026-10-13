#!/usr/bin/env python3
"""
Purpose: produce an advisory conversational-GPT candidate classification from source instructions.
When used: after canonical source instructions are extracted and before CustomGPT-to-Skill target generation.
Why it exists: make obvious persistence/persona signals reproducible while keeping the final classification and drift policy human-gated.
Inputs/parameters: one UTF-8 text/Markdown instruction file.
Outputs: JSON with candidate classification, matched strong/weak signals, and a note that human confirmation is mandatory for conversational or ambiguous results.
High-level behaviour: scan normalized source text for explicit multi-turn, identity-persistence, exit/reset, state, anti-drift, and weak conversational cues; classify conservatively from the resulting evidence.
Failure semantics: never edits source files, exits non-zero for missing/unreadable input, and never authorizes conversion or chooses a drift policy.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

STRONG = {
    "persistent_identity": r"\b(persist(?:ent|ence)|remain|maintain|keep|stay)\b.{0,80}\b(identity|persona|role|character|mode)\b",
    "multi_turn": r"\b(across turns|later turns|next turn|follow[- ]?up|multi[- ]?turn|conversation|session)\b",
    "explicit_exit": r"\b(exit|deactivate|disable|leave|stop using|reset)\b.{0,80}\b(persona|role|mode|assistant|identity|session)\b",
    "state_machine": r"\b(state machine|stateful|state transition|routing state|conversation state)\b",
    "anti_drift": r"\b(drift|anti[- ]?drift|recover(?:y)?|restore identity|generic assistant)\b",
}

WEAK = {
    "conversation_starters": r"\bconversation starters?\b",
    "generic_role": r"\b(you are|act as)\b.{0,100}\b(expert|assistant|advisor|reviewer|coach)\b",
    "friendly_tone": r"\b(friendly|conversational|warm|empathetic|casual) tone\b",
}

def matches(text: str, patterns: dict[str, str]) -> list[str]:
    return [name for name, pattern in patterns.items() if re.search(pattern, text, re.IGNORECASE | re.DOTALL)]

def classify(strong: list[str], weak: list[str]) -> str:
    if len(strong) >= 2 or "persistent_identity" in strong or "anti_drift" in strong:
        return "CONVERSATIONAL_CANDIDATE"
    if len(strong) == 1 and weak:
        return "AMBIGUOUS"
    if not strong and len(weak) >= 2:
        return "AMBIGUOUS"
    return "NON_CONVERSATIONAL_CANDIDATE"

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("instruction_file")
    args = parser.parse_args()
    path = Path(args.instruction_file)
    if not path.is_file():
        raise SystemExit(f"input file not found: {path}")
    text = path.read_text(encoding="utf-8", errors="replace")
    strong = matches(text, STRONG)
    weak = matches(text, WEAK)
    result = {
        "classification": classify(strong, weak),
        "strong_signals": strong,
        "weak_signals": weak,
        "human_confirmation_required": classify(strong, weak) in {"CONVERSATIONAL_CANDIDATE", "AMBIGUOUS"},
        "note": "Advisory only. Never choose persona-drift policy or host continuity automatically.",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
