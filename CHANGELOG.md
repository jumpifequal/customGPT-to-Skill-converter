# Changelog

**Repository packaging (skill version unchanged: 10.7.0)**

- add: GitHub repository layout — the skill package sits at the repository root; `SKILL.md`, `agents/`, `assets/`, `references/` and `scripts/` are byte-identical to the 10.7.0 skill archive.
- add: `README.md` (English) and `README.it.md` (Italiano) covering motivation, plugin limits and when a skill derived from a Custom GPT is the better choice.
- add: `docs/` (architecture, decision gates, runtime tools, examples) and the repository logo under `docs/assets/`.
- add: `CONTRIBUTING.md`, `SECURITY.md`, `.gitignore`, `requirements-dev.txt`.
- add: `tools/validate_repo.py` and GitHub Actions workflow running the repository checks plus the skill's own regression suite.
- change: `changelog.md` renamed to `CHANGELOG.md` (GitHub convention; avoids case-insensitive filename collisions). Content below is unchanged.

**10.7.0 - Human-in-Control conversion decisions**

- add: decision awareness — every consequential conversion choice is explained with rationale and practical consequences before the user is asked to confirm it.
- add: global human confirmation — target generation is blocked until all applicable migration choices are explicitly confirmed by the user.
- add: conversion parameter report — every conversion shows and preserves a deterministic table of selected parameters, origin, rationale, and practical consequence.
- change: batch approval — users may confirm all recommended non-destructive choices together only after every option and consequence has been shown.

**10.6.0 - Migration fidelity, control-plane preservation, and reusable validation harnesses**

- add: control-plane migration — layered CustomGPT architectures can preserve canonical originals while using runtime-native operational representations with explicit bootstrap, dependency, and parity tracking.
- add: Knowledge migration — source Knowledge files are preserved byte-for-byte when possible, indexed with hashes, and kept distinct from non-authoritative derived access representations.
- add: DOCX migration gate — DOCX files require an explicit preservation strategy, with semantic-loss acknowledgement before destructive replacement.
- add: conversational migration — conversational or mixed GPTs require human confirmation of conversational scope, persona-drift handling, and host-continuity assumptions before conversion proceeds.
- add: validation harness templates — reusable Core Harness plus task-family profiles are available for classifier/router, extraction, RAG/research, conversational, workflow, evaluator, coding, creative, and hybrid GPTs.
- add: harness approval gate — existing source harnesses are preserved, while newly proposed harnesses require explicit human approval before insertion.
- add: package-size gate — projected Skill archives over 25 MiB trigger a human decision before any compression, externalization, or fidelity-reducing transformation.
- change: icon handling — non-square source icons are proportionally reframed to fill the 64×64 square without top/bottom or side bands.
- change: metadata naming — the Skill display/title name is `CustomGPT-to-Skill`; versioning is kept separate from the name.
- change: decision traceability — human migration choices are recorded and validated deterministically before generation or packaging continues.


**10.5.0 - Layered control-plane migration**

- add: control-plane detection — source artifacts are classified as passive Knowledge, operational control, or mixed based on behaviour and cross-file dependencies rather than filename or extension.
- add: dual-runtime fidelity — operational artifacts can preserve canonical originals while using native or derived runtime representations according to target compatibility.
- add: control-plane human gate — layered GPTs require explicit confirmation of the migration strategy before target generation.
- add: bootstrap preservation — source-defined precedence, dependency order, routing, state, and override semantics are preserved explicitly in the converted Skill.
- add: behavioural parity — layered conversions track representative bootstrap, routing, precedence, fallback, and output-contract scenarios before behavioural equivalence is claimed.
- change: operational DOCX handling — preserving a control-plane DOCX without a runtime representation is treated as a runtime-risk choice rather than the safest default.


**10.4.0 - Knowledge and document fidelity**

- add: byte-preserving Knowledge migration — CustomGPT Knowledge files are preserved unchanged when possible and indexed with path, media type, size, and SHA-256 provenance.
- add: DOCX fidelity gate — users choose whether to preserve the original only, preserve plus a derived retrieval representation, or replace the original with explicit semantic-loss acknowledgement.
- add: package-size decision gate — Skills projected above 25 MiB require an explicit lossless, externalization, lossy, or abort decision before content is altered.
- add: deterministic decision record — human migration choices are stored and validated before conversion proceeds.
- change: derived document representations — Markdown, text, or JSON derivatives are treated as access aids rather than authoritative replacements for the source document.


**10.3.0 - Square icon reframing**

- change: non-square icon conversion — source icons are proportionally cover-cropped into the 64×64 frame so the final icon has no top/bottom or side bands.
- change: icon focus — reframing prefers the visible-content center when transparency makes foreground bounds detectable, otherwise it uses the geometric center.
- change: SVG normalization — non-square SVG sources are rasterized without distortion and then reframed with the same square-cover rule.


**10.2.0 - Human-aware conversational decisions**

- change: conversational gate guidance — each classification, persona-drift, and host-continuity option is explained in plain language before the user is asked to choose.
- change: conversational reply contract — the final approval remains compact and machine-readable after the rationale is shown.
- add: decision-awareness regression — conversion checks preserve the requirement that human approval be informed rather than label-only.


**10.1.0 - Conversational GPT migration**

- add: conversational detection — the converter identifies conversational, non-conversational, and ambiguous CustomGPT patterns using persistent identity, multi-turn, exit, state, and anti-drift signals.
- add: mandatory conversational confirmation — conversational or ambiguous sources pause before target generation until the user confirms YES, NO, or MIXED.
- add: persona-drift strategies — users can choose strict lock, bounded lock, no lock, or a custom persistence contract.
- add: host-continuity choices — conversational conversion distinguishes host-dependent, host-guaranteed, and turn-scoped continuity without claiming unsupported cross-turn persistence.
- add: session-lock adaptation — approved conversational Skills can include silent drift detection, recovery, exit handling, and deterministic validation while preserving the original user experience.
- change: mixed GPT handling — persona locking can be scoped only to the approved conversational surface while leaving unrelated one-shot or tool modes unlocked.


**10.0.0 - Initial CustomGPT-to-Skill conversion framework**

- add: CustomGPT-to-Skill conversion — CustomGPT instruction bundles, Knowledge assets, metadata, icons, and runtime assumptions can be migrated into a validated Universal Skill package.
- add: preservation-first conversion — source behaviour, Knowledge completeness, tool assumptions, output contracts, failure semantics, and compatible existing code are preserved unless an explicit adaptation is required.
- add: recursive source inventory — source assets are inventoried with hashes so unexplained omissions can be detected before delivery.
- add: conversion-gap reporting — unavailable tools, actions, secrets, connectors, or runtime capabilities are surfaced as explicit gaps instead of being invented.
- add: regression-safe evolution — conversion behaviour is tracked through a feature-invariant ledger and representative target validation.
- add: package validation — generated Skills validate required structure, metadata references, icon assets, helper discipline, package hygiene, and source-to-target preservation evidence before release.
- add: icon normalization — supplied icons are converted into a physical 64×64 PNG and a self-contained SVG without external image dependencies.
- fix: Knowledge completeness — conversions no longer rely on prior package contents when the source bundle contains additional Knowledge files.
- fix: icon metadata integrity — icon references are validated so packaged metadata cannot point to a missing asset.

