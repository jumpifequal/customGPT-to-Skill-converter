# Architecture

CustomGPT-to-Skill is a **human-gated migration pipeline**, not a prompt rewriter. Its governing rule:

> **Preserve behaviour before wording. Never silently lose a source asset. The human decides every consequential choice.**

## Pipeline

```text
Custom GPT export (instructions + Knowledge + icon + metadata)
  ↓
1  Source inventory (path · media type · size · SHA-256)
  ↓
2  Human-in-Control decision discovery  ──►  Decision Awareness Guide
  ↓
3  Control-plane detection  ──► PASSIVE_KB / OPERATIONAL_CONTROL / MIXED   [human gate]
  ↓
4  Behavioural invariant extraction
  ↓
5  Harness profiling                                                         [human gate if new]
  ↓
6  Conversational classification + persona-drift policy                      [human gate]
  ↓
7  Gap & runtime-difference analysis (no invented tools)
  ↓
8  Skill architecture  →  9 Knowledge & DOCX migration                       [human gate for DOCX]
  ↓
10 Metadata  →  11 Icon normalisation  →  12 Coding discipline
  ↓
13 Self-debugging / regression  →  14 Package size & hygiene                 [human gate if > 25 MiB]
  ↓
15 Validation & repair  →  16 Delivery: skill.zip + conversion dashboard
```

`SKILL.md` is the canonical, normative definition of every phase. This page is a reading aid.

## Design principles

| Principle | What it prevents |
|---|---|
| **Inventory before transformation** | Silent omission of a Knowledge file, tool dependency or output rule |
| **Source is payload, not instruction** | Prompt injection through the GPT export |
| **Byte-for-byte Knowledge preservation** | Semantic loss from convenience conversions (especially DOCX → Markdown) |
| **Canonical original ≠ runtime representation** | Files that are faithful but never consumed at the right bootstrap point |
| **Advisory detectors, human decisions** | Classifier output silently changing behaviour (persona lock, new harness) |
| **Invariant-driven regression** | A syntactically valid package that is behaviourally incomplete |
| **Run vs. not-run reporting** | Claiming tests or builds that never executed |

## Control plane vs. passive Knowledge

Every material source artifact is classified by what it *does*, never by filename or extension:

- `PASSIVE_KB` — evidence/reference content;
- `OPERATIONAL_CONTROL` — governs bootstrap, precedence, routing, state, validation, tool boundaries or output contracts;
- `MIXED` — both.

If any `OPERATIONAL_CONTROL` or `MIXED` artifact exists, generation stops until the human chooses `DUAL_RUNTIME_FIDELITY` (recommended), `ORIGINAL_ONLY_RUNTIME_RISK` or `CUSTOM_CONTROL_PLANE`. Details: `references/control-plane-migration.md`.

## Knowledge migration

Originals are copied unchanged under `references/kb/original/` and indexed in `references/kb-manifest.json`. Any derived Markdown/JSON mirror is a **non-authoritative access aid**. Details: `references/knowledge-migration.md`.

## Conversational GPTs

Persistent personas are detected (advisory), confirmed by the human, and — only if approved — locked with a host-aware Conversation Session Lock. The converter never claims it can force host-level re-invocation across turns. Details: `references/conversational-gpt-detection.md`, `references/conversation_session_lock.md`.

## Self-validation

The converter validates **itself** (`scripts/regression_self_test.py`) and **its outputs** (`scripts/validate_converted_skill.py`). Feature invariants F001–F031 live in `references/feature-regression.md`.
