# Contributing

Contributions must preserve the converter's central invariant:

> **The human controls every consequential migration choice, and no source asset is silently lost.**

## Before changing execution logic

1. Identify the behavioural invariant you are changing (see `references/feature-regression.md`).
2. Explain the failure mode the change addresses.
3. Do not weaken a human gate (Human-in-Control, control-plane, conversational, DOCX, harness, package-size) to make conversions faster.
4. Preserve byte-for-byte Knowledge migration and the hash-addressed KB manifest.
5. Add or update a regression invariant **before** shipping a new feature (`references/feature-regression.md` + `scripts/regression_self_test.py`).
6. Keep helper scripts self-describing: every operational helper begins with a module docstring stating purpose, when used, why it exists, inputs, outputs, behaviour and failure semantics.

## Validation

```bash
python -m pip install -r requirements-dev.txt
python tools/validate_repo.py
```

`tools/validate_repo.py` checks the repository layout and then runs the skill's own `scripts/regression_self_test.py` and `scripts/validate_converted_skill.py`. SVG icon sources additionally need `cairosvg` (not required for the test suite).

## Documentation changes

Documentation may explain the skill in simpler language but must not contradict `SKILL.md` or the files under `references/`. When in doubt, the skill package is canonical.

## Repository conventions

- The skill package lives at the repository root (`SKILL.md`, `agents/`, `assets/`, `references/`, `scripts/`).
- `docs/assets/logo.*` is the repository logo; `assets/icon.*` is the **skill UI icon** and is validated at 64×64. Do not mix them.
- Never commit source GPT exports or conversion workspaces.
