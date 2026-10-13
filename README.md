# CustomGPT-to-Skill

<p align="center">
  <img src="docs/assets/logo.svg" alt="CustomGPT-to-Skill logo" width="180">
</p>

<p align="center">
  <a href="#install"><img alt="Install with npx" src="https://img.shields.io/badge/install-npx%20skills%20add-CB3837"></a>
  <img alt="Skill version" src="https://img.shields.io/badge/skill-10.7.0-2F6BFF">
  <a href="README.it.md"><img alt="Italiano" src="https://img.shields.io/badge/lingua-italiano-009246"></a>
</p>

Convert a **Custom GPT** (instructions + Knowledge files + icon + metadata) into a **Universal Skill** package (`SKILL.md` open format) — without silently losing behaviour, files, or control.

It is designed around one principle:

> **Preserve behaviour before wording. Never lose an asset silently. The human decides every consequential choice.**

🇮🇹 [Leggi in italiano](README.it.md)

---

## Why this exists

A Custom GPT is easy to build and hard to *own*. Over months it accumulates real engineering: refusal boundaries, output contracts, fallback rules, a curated Knowledge base, sometimes a layered "control plane" of files that tell the model what to load, in which order, and who wins on conflict. All of that lives inside one vendor UI, cannot be diffed, reviewed, hashed, versioned, or tested in CI, and is capped by the platform (a limited number of Knowledge files per GPT, retrieved through a pipeline you cannot inspect — check the current OpenAI Help Center for exact figures).

Skills fix the ownership problem: a folder of plain files (`SKILL.md`, `references/`, `scripts/`, `assets/`) that lives in Git and is loaded on demand by agent runtimes that support the open format.

But **copy-pasting a GPT's system prompt into a `SKILL.md` is not a migration**. Naive ports routinely:

- drop Knowledge files, or flatten them (DOCX → Markdown loses comments, tracked changes, fields, tables, reading order);
- keep the files but lose *when* they are read (bootstrap order, precedence, routing, state machines);
- turn a persistent persona into a one-shot prompt;
- reference icons or tools that were never packaged or never existed in the target runtime;
- claim "it works" with nothing to check it against.

CustomGPT-to-Skill turns that migration into an **auditable, human-gated, regression-tested process**:

| Concern | What the skill does |
|---|---|
| Nothing lost | Hash-based source inventory (path, media type, size, SHA-256) and source→target manifest comparison that fails on unexplained omissions |
| Knowledge fidelity | Byte-for-byte preservation under `references/kb/original/` + `kb-manifest.json`; derived mirrors are non-authoritative |
| Layered GPTs | Detects `PASSIVE_KB` / `OPERATIONAL_CONTROL` / `MIXED` artifacts; preserves canonical originals *and* a runtime-executable representation, with bootstrap order and parity checks |
| Persistent personas | Advisory detection + human confirmation + optional host-aware Conversation Session Lock (never claims it can force host re-invocation) |
| Validation harness | Preserves any existing source harness; proposes a task-family harness only with explicit approval |
| Human control | Every consequential choice is explained (rationale + practical consequence) *before* you are asked; a deterministic **Conversion Parameter Report** shows what was selected and why |
| Honest reporting | The delivery dashboard separates validation *run* from *not run* and lists unsupported capability gaps |
| Regression safety | 31 feature invariants (F001–F031) and a self-test suite guard the converter itself |

## Plugins vs. a skill born from your GPT

"Just use a plugin" is a common answer to "how do I reuse this GPT elsewhere?". Plugins are the right tool for some jobs — and the wrong one for this.

**What plugins are good at:** giving an agent *access* — live data, SaaS APIs, write actions with side effects. A skill can *call* those; the two are complementary, not competing.

**Where plugin-style integrations fall short for migrating a GPT:**

1. **They carry access, not method.** What makes a GPT valuable is its *behaviour*: scoping, gates, refusal rules, output contracts, failure semantics. A plugin exposes tools; it has no natural place for "do these steps in this order and stop if this check fails".
2. **Runtime and vendor coupling.** Plugins hook into a specific harness or marketplace. Lifecycle risk is real — ChatGPT's original plugin system was retired in favour of GPTs and Actions, and integrations tied to a single runtime inherit that fragility.
3. **Opacity.** Remote endpoints, marketplace updates and tool descriptions can change under you. A skill is local text and scripts: diffable, reviewable, hashable, pinned by commit.
4. **Data egress and approval friction.** Plugins and connectors usually send data to a third party and require organisation-level approval. For sensitive or regulated material, "local files and deterministic scripts" is often the only acceptable shape.
5. **Coarse granularity.** A plugin is installed as a unit and selected by tool descriptions. It cannot express layered control planes, persona-persistence policies, or per-gate human confirmation.
6. **No place for a preserved corpus.** Byte-exact Knowledge with a hash manifest, loaded selectively, is a file-layout concern — not something a connector provides.
7. **Not testable offline.** A skill repo can run regression checks in CI on every commit. A hosted integration is hard to pin and hard to reproduce.

**Why a skill derived from the old GPT is often the better starting point:**

- **You already paid for the iterations.** The GPT's instructions encode behaviour that was tested against real usage. Preserving that contract is cheaper and safer than re-deriving it from scratch.
- **Your Knowledge base gets out of the cage.** Files live in the repo with provenance, instead of behind a capped upload slot and an opaque retriever.
- **Portability.** `SKILL.md` is an open, folder-based format supported by a growing number of agent runtimes, so the same package is not tied to the product it was born in.
- **Progressive disclosure.** The skill's description is the standing context cost; detail in `references/` loads only when needed.
- **Determinism where it counts.** Hashing, validation, size gates and icon normalisation are scripts, not model improvisation.
- **Ownership.** Git history, code review, CI and a changelog.

**When *not* to migrate a GPT with this tool:** the GPT's value is mostly its live **Actions** with OAuth and side effects (re-create those as connectors/MCP and keep the skill for method); you depend on GPT Store distribution or monetisation; you rely on voice/mobile UX or platform memory; or the target runtime cannot run bundled scripts. The skill reports such cases as explicit **conversion gaps** instead of inventing substitutes.

> Skills are not risk-free: they run with the permissions of the agent that loads them (often a shell). Read any skill — including conversions produced by this one — before installing it. See [SECURITY.md](SECURITY.md).

## What it does

Given a Custom GPT export (ZIP, or instruction document + Knowledge files), the skill:

1. inventories every source asset with SHA-256;
2. identifies the canonical instruction source by *content*, not filename;
3. extracts behavioural invariants (trigger · required behaviour · forbidden shortcut · output obligation · preservation evidence);
4. classifies control-plane artifacts and, if needed, stops for a human strategy choice;
5. detects/preserves harness controls; proposes new ones only with approval;
6. classifies conversational GPTs and gates persona-drift handling;
7. preserves Knowledge byte-for-byte; gates DOCX handling and any size reduction;
8. builds `SKILL.md`, `agents/openai.yaml`, icons (`icon.png` 64×64 + self-contained `icon.svg`) and only the supporting files that materially help;
9. runs regression and structural validation and compares source vs. target manifests;
10. delivers `skill.zip` plus a conversion dashboard.

## Core workflow

```text
Custom GPT export
  ↓
Source inventory (SHA-256)
  ↓
Human-in-Control: Decision Awareness Guide → explicit confirmation
  ↓
Control-plane · Harness · Conversational · DOCX gates
  ↓
Conversion Parameter Report (deterministic, shown to the user)
  ↓
Target generation (Skill + KB originals + icons)
  ↓
Regression · structural validation · manifest comparison · size gate
  ↓
skill.zip + conversion dashboard
```

## Install

Install directly from GitHub with the open `skills` CLI:

```bash
npx skills add jumpifequal/customgpt-to-skill
```

Inspect what the CLI detects before installing:

```bash
npx skills add jumpifequal/customgpt-to-skill --list
```

Install globally for a specific agent:

```bash
npx skills add jumpifequal/customgpt-to-skill -g -a codex -y
npx skills add jumpifequal/customgpt-to-skill -g -a claude-code -y
```

Install from a local clone:

```bash
git clone https://github.com/jumpifequal/customgpt-to-skill.git
cd customgpt-to-skill
npx skills add .
```

Verify the repository before installation or contribution:

```bash
python -m pip install -r requirements-dev.txt
python tools/validate_repo.py
```

> `npx skills add` installs the skill. The repository itself does not require `npm install`; Node.js/npm are only needed to run the `skills` CLI. SVG icon sources additionally need `cairosvg` (not needed for the test suite).

## Quick start

Attach your Custom GPT export (or instructions + Knowledge files + optional icon) and say:

```text
Use $customgpt-to-skill to convert my attached Custom GPT export into a validated Universal Skill package.
```

Typical natural triggers: *convert / port / migrate / rebuild this Custom GPT as a Skill*; *turn this GPT export into a skill*; *re-run my GPT-to-skill conversion with the new Knowledge files*.

You will be walked through a **Decision Awareness Guide**; nothing is generated until you confirm.

## Helper modules

| Script | Purpose |
|---|---|
| `build_inventory.py` | Deterministic source/target inventory with hashes |
| `kb_preserve.py` | Byte-for-byte Knowledge migration + manifest |
| `icon_convert.py` | Safe PNG/SVG icon normalisation |
| `detect_conversational_gpt.py` | Advisory conversational classification |
| `harness_profile_selector.py` | Advisory harness-family recommendation |
| `decision_gate_guard.py` | Validates all human gates |
| `render_parameter_report.py` | Renders/validates the Conversion Parameter Report |
| `control_plane_guard.py` | Validates control-plane map and parity |
| `conversation_lock_guard.py` | Validates conversation-lock integrations |
| `package_size_guard.py` | Projected compressed size vs. 25 MiB |
| `validate_converted_skill.py` | Structural/semantic validation of a generated skill |
| `regression_self_test.py` | Converter self-regression (F001–F031) |

## Repository structure

```text
customgpt-to-skill/
├── .github/
│   └── workflows/
│       └── validate.yml
├── agents/
│   └── openai.yaml
├── assets/
│   ├── icon.png          # skill UI icon (64×64)
│   └── icon.svg
├── docs/
│   ├── assets/
│   │   ├── logo.png      # repository logo
│   │   └── logo.svg
│   ├── architecture.md
│   ├── decision-gates.md
│   ├── examples.md
│   └── runtime-tools.md
├── references/           # normative conversion policies
├── scripts/              # deterministic helpers + regression suite
├── tools/
│   └── validate_repo.py
├── CHANGELOG.md
├── CONTRIBUTING.md
├── README.md
├── README.it.md
├── SECURITY.md
├── SKILL.md              # entry point
└── requirements-dev.txt
```

## Documentation

- [Architecture](docs/architecture.md)
- [Decision gates](docs/decision-gates.md)
- [Runtime tools](docs/runtime-tools.md)
- [Usage examples](docs/examples.md)
- [Changelog](CHANGELOG.md)

## Design constraints

The skill deliberately prefers:

- a human decision over a silent default;
- preserved originals over convenient conversions;
- explicit conversion gaps over invented capabilities;
- invariant-driven regression over schema-only validity;
- "validation not run" over an unverifiable "validated".

## Version

Skill `10.7.0` — see [CHANGELOG.md](CHANGELOG.md).

Author: **Enrico Frumento**

## License

No license is declared in the source skill. Add the license appropriate for your intended publication and redistribution policy before public release if required.
