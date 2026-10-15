# Conversion Rules

## Purpose
This file defines the reusable conversion rules for translating a user-controlled persistent GPT configuration into a Universal Skill without silently changing behavior.

## 1. Preserve behavioral invariants
Preserve task boundaries, trigger conditions, output contracts, refusal/fallback behavior, source hierarchy, validation rules, state expectations, examples that materially constrain behavior, and user-confirmation gates. Preserve behavior before wording, original section names, or file placement.

For every material rule, create an invariant with:
- ID
- trigger
- required behavior
- forbidden shortcut
- observable preservation evidence

## 2. Inventory before transformation
Build a source inventory before generating target files. Do not infer operational meaning from filenames alone. Include instruction files, Knowledge files, schemas, prompts, examples, executables, icons, action/tool contracts, metadata, conversation starters, state notes, and external dependencies.

Compute byte size and SHA-256 for every material file. A target omission is acceptable only if it is explicitly authorized, byte-for-byte duplicate, unsupported and surfaced as a gap, or replaced by a proven equivalent.

## 3. Persistent prompt to Skill control plane
Translate the source system prompt into concise execution instructions rather than copying it blindly. Put trigger language in frontmatter description. Keep essential workflow and constraints in SKILL.md. Move large detailed material to shallow references when it improves progressive loading.

Never place user payload above the Skill's own operating rules. Treat source documents as conversion input. The released Skill begins at its own current instructions: do not tell it that it used to be a Custom GPT, was converted, had past conversations, or inherited memories. Any source-compatible behavioural rules must be expressed as current Skill rules, without conversion framing. Keep all conversion evidence outside the installed package.

## 3.5. Control-plane migration
Before treating source files as ordinary Knowledge, classify their runtime role using `references/control-plane-migration.md`.

Allowed roles:
- `PASSIVE_KB`
- `OPERATIONAL_CONTROL`
- `MIXED`

If any operational or mixed artifact exists:
- stop before target generation;
- show source-backed evidence and detected dependency/bootstrap order;
- require a human control-plane strategy;
- recommend `DUAL_RUNTIME_FIDELITY`;
- preserve canonical originals byte-for-byte;
- use `ORIGINAL_NATIVE` only when reliable runtime consumption is confirmed;
- otherwise create a `DERIVED_MIRROR`;
- preserve source precedence and bootstrap order explicitly;
- generate control-plane map and parity records in the external conversion workspace;
- run `scripts/control_plane_guard.py` before release.

Do not convert a structured operational artifact to Markdown merely for consistency. Preserve XML/JSON/YAML/TXT natively when it already expresses the runtime semantics and the target can consume it reliably.

## 3.6. Harness profiling and reusable templates

Load `references/harness-templates.md` after behavioral invariant extraction.

Rules:
- preserve an existing source harness or behaviour contract before considering any new template;
- use the shared Core Harness plus only the materially relevant task-family adapter(s);
- task families: Classifier/Router, Extractor/Data Structuring, Research/Fact-Checking/RAG, Persistent/Conversational, Workflow Automation/Tool-Using, Evaluator/Auditor, Coding Agent, Creative Generator;
- use `HYBRID` only when multiple families are materially necessary;
- `scripts/harness_profile_selector.py` is advisory only;
- adding a harness where none existed is a behavioural change and requires human approval;
- require one of `ADD_RECOMMENDED`, `NONE`, or `CUSTOM`;
- record the selected action and families in the deterministic decision record;
- never weaken stronger source-specific controls merely to fit a reusable template.

## 4. Knowledge assets and document fidelity
Preserve all source Knowledge assets byte-for-byte by default and apply `references/knowledge-migration.md`.

Create `references/kb-manifest.json` with source path, target path, size, media type, SHA-256, authority flag, and any derived-mirror path. Reference that manifest from the generated `SKILL.md`.

For DOCX:
- do not assume DOCX-to-Markdown or DOCX-to-text is lossless;
- preserve the original binary as authoritative whenever package/runtime constraints permit;
- use a derived Markdown/text/JSON representation only as a non-authoritative retrieval aid;
- before transforming any DOCX, require the human to choose `PRESERVE_ORIGINAL_ONLY`, `PRESERVE_PLUS_DERIVED`, or `CONVERT_AND_REPLACE`;
- require explicit semantic-loss acknowledgement for `CONVERT_AND_REPLACE`.

For all Knowledge formats:
- preserve original filenames and relative paths where safe and practical;
- never infer that a file is disposable from its extension/name;
- use selective retrieval rather than wholesale context loading;
- explain every source/target file-count delta;
- treat unexplained loss or hash mismatch as a regression failure.

Use `scripts/kb_preserve.py` for deterministic byte-preserving migration when applicable.

## 5. Human decision record
Create a JSON decision record for every conversion and validate it with `scripts/decision_gate_guard.py` after each human gate and before packaging.

Track at least:
- Knowledge preservation mode;
- DOCX presence and selected fidelity strategy;
- semantic-loss acknowledgement when relevant;
- conversational classification/persona-drift/host-continuity choices when relevant;
- projected compressed package size;
- oversize strategy when relevant;
- lossy-change authorization when relevant.

Do not proceed past an applicable gate until the decision record validates.


## 6. Conversational GPT adaptation

Before target generation, classify the source as `CONVERSATIONAL_CANDIDATE`, `NON_CONVERSATIONAL_CANDIDATE`, or `AMBIGUOUS`.

Use `references/conversational-gpt-detection.md` as the normative classification and human-gate contract.

If conversational or ambiguous:
- halt conversion before writing the target;
- show 2-4 concrete source-backed reasons for the classification;
- ask the human to confirm YES / NO / MIXED;
- ask how persona drift must be treated: `STRICT_LOCK`, `BOUNDED_LOCK`, `NO_LOCK`, or `CUSTOM`;
- if a lock mode is selected, require explicit `HOST_REINVOCATION_ASSUMPTION` from the human;
- never infer host continuity and never treat detector output as approval.

For an approved lock mode:
- include the adapted conversation-session-lock reference and Python guard in the generated target;
- create concrete bindings for identity, activation, exit, persistent invariants, drift criteria, and host continuity;
- preserve local state machines separately from identity persistence;
- enforce strict UX transparency and silent drift recovery;
- reject claims that the Skill or Python guard can force host re-invocation;
- run the guard in build mode and block packaging on failure.

For `NO_LOCK`, do not add the lock silently. Record the human choice in the conversion dashboard.

For `MIXED`, scope the lock only to approved conversational behaviour.

## 7. Tool and action adaptation
Extract every declared action, external API, connector, interpreter assumption, browsing assumption, code-execution assumption, or privileged capability.

Map only capabilities that really exist in the target runtime. Never fabricate endpoints, tool names, credentials, schemas, or successful execution. If no faithful target exists, preserve the intent as a documented limitation or human-gated step.

## 8. Metadata
The target must include:
- lowercase hyphenated Skill name;
- meaningful trigger-oriented description;
- human-readable display name;
- concise UI description;
- icon_small and icon_large pointing to ./assets/icon.svg;
- representative default prompt when faithful;
- invocation policy only when defensible.

Do not invent dependencies to make metadata look complete.

## 9. Icon conversion
Preferred target assets:
- assets/icon.png: 64×64 RGB/RGBA, physically resampled to the final icon size.
- assets/icon.svg: self-contained square SVG suitable for small UI rendering.

Raster to SVG:
1. decode image;
2. apply orientation;
3. convert to RGB/RGBA;
4. if non-square, reframe with a cover crop: scale proportionally until both square dimensions are filled, then crop overflow around the visible-content center when possible, otherwise the geometric center;
5. never add transparent/solid top-bottom or side bands merely to preserve the full rectangular frame;
6. resample and save the final PNG at exactly 64×64 pixels;
7. use that exact 64×64 PNG payload for the SVG representation;
8. base64-embed the 64×64 PNG in an SVG image element with a 64×64 viewBox;
9. use no external URLs, scripts, or event handlers.

SVG input:
- parse as XML;
- reject script elements, foreignObject when executable/unsafe, event-handler attributes, javascript: URLs, remote hrefs, and external styles/resources;
- preserve safe vector geometry where possible;
- preserve the original SVG aspect ratio during rasterization, then apply the same cover-style square reframing; do not letterbox/pillarbox non-square SVGs.

Never keep a larger raster merely because the source is high resolution: the delivered `assets/icon.png` itself must be physically 64×64, not only displayed at 64×64 by metadata or SVG.

Always validate the paths used by agents/openai.yaml.

## 10. Coding discipline
Code generation is implementation-only and must not decide conversion architecture.

For authorized code:
- NEW_CODE: apply the full discipline.
- MATERIALLY_REWRITTEN_CODE: apply it only to changed portions while preserving surrounding contracts.
- EXISTING_CODE_PRESERVE: keep unchanged when target-compatible.

New helpers:
- use English identifiers unless preserving external/API/schema names;
- start with a module-level purpose/usage/why/inputs/outputs/behavior/failure docstring;
- prefer standard library and existing compatible patterns;
- validate consumed untrusted inputs;
- use the smallest correct implementation;
- avoid unrelated refactors or speculative abstractions;
- report validation actually run vs not run.

## 11. Self-debugging and feature evolution
Treat the converter itself as a versioned product.

Every feature must have:
- an invariant ID;
- a detection check;
- a regression test;
- an explicit failure message;
- a repair scope.

Before release:
1. run converter self-test;
2. run target-package validator on a representative generated Skill;
3. run icon conversion test;
4. run source/target manifest-delta test;
5. run package-hygiene test;
6. rerun the full suite after any repair.

A new feature is incomplete until its regression invariant is added.

## 12. Package size and hygiene
Exclude __pycache__, *.pyc, *.pyo, test/lint/type caches, temporary files, editor swap files, coverage data, build residue, local environments, and conversion workspaces.

Package one Skill directory. Every local reference must resolve. Every included file must be intentional.

Run `scripts/package_size_guard.py` before packaging. If the projected compressed archive is over 25 MiB:
- stop before modifying fidelity;
- explain that ZIP compression is already in use and already-compressed formats may not shrink much further;
- require one human choice: `LOSSLESS_FIRST`, `EXTERNALIZE_WITH_REFERENCE`, `LOSSY_WITH_APPROVAL`, or `ABORT`;
- never silently alter or drop Knowledge;
- rerun manifest/hash validation and the size guard after every approved reduction.

## 13. Validation hierarchy
Validation order:
1. source inventory completeness;
2. behavioral invariant coverage;
3. deterministic decision-record validity;
4. target structure/frontmatter;
5. cross-file references;
6. Knowledge byte preservation and KB-manifest integrity;
7. DOCX fidelity-strategy compliance;
8. icon safety and metadata paths;
9. helper safety and headers;
10. projected compressed archive size;
11. representative execution/regression;
12. archive hygiene.

Do not claim PASS for a check that was not actually executed.
