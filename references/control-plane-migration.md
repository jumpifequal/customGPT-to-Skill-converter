# Control-Plane Migration

## Purpose

Use this policy when a Custom GPT contains multiple instruction layers, state machines, orchestration files, meta-prompts, policy documents, or other resources that govern runtime behaviour.

The governing principle is:

**Preserve canonical source fidelity and runtime executability separately.**

A byte-perfect source archive is not sufficient if the target Skill cannot apply the governing instructions at the correct time. A runtime-native rewrite is not sufficient if the canonical original is lost or cannot be audited later.

## Artifact role classification

Classify every material source artifact by runtime role:

- `PASSIVE_KB` — evidence/reference content that does not govern routing, priority, state, persona persistence, execution policy, or output contracts.
- `OPERATIONAL_CONTROL` — content that directly governs bootstrap, precedence, routing, state transitions, mode selection, validation, tool boundaries, output contracts, or other runtime behaviour.
- `MIXED` — one artifact contains both passive Knowledge and operational control semantics.

Do not classify from filename or extension alone. Inspect content and cross-file invocation relationships.

## Control-plane detection signals

Strong signals include:

- another source file explicitly says to load/read/invoke this artifact before responding;
- explicit state machine, router, dispatcher, precedence, visibility, mode, or transition logic;
- global output validators or mandatory pre-flight behaviour;
- named policies that override or constrain downstream instruction layers;
- persistent persona/session rules;
- appendices/templates/modules invoked dynamically by another control artifact;
- an artifact that defines the authoritative execution order for other files.

Weak signals alone are not enough:

- a file is named "prompt", "config", "rules", or "instructions";
- a DOCX contains prose;
- a JSON/XML file exists;
- a file is large or highly structured.

## Human control-plane gate

If any artifact is classified `OPERATIONAL_CONTROL` or `MIXED`, stop before target generation and show the user:

1. which artifacts appear operational and why;
2. the detected dependency/bootstrap order;
3. the fidelity/runtime trade-off.

Then ask the human to confirm one strategy:

- `DUAL_RUNTIME_FIDELITY` — recommended. Preserve every canonical original byte-for-byte. Use the original directly when the target can reliably consume that format at runtime; otherwise generate a separate operational mirror. Preserve provenance and test the resulting control flow.
- `ORIGINAL_ONLY_RUNTIME_RISK` — preserve originals without operational mirrors. This maximizes source fidelity but may break runtime behaviour when the target does not reliably load/interpret the original at the required execution point.
- `CUSTOM_CONTROL_PLANE` — human specifies per-artifact runtime mode, bootstrap order, and any exceptions.

The gate must include the short rationale above before collecting the compact answer.

Do not silently choose `ORIGINAL_ONLY_RUNTIME_RISK`.

## Canonical source and runtime representation

For each control-plane artifact, record:

- `source_path`
- `artifact_role`
- `canonical_target_path`
- `canonical_sha256`
- `runtime_representation_mode`
- `runtime_target_path`
- `runtime_format`
- `depends_on`
- `precedence_level`
- `runtime_native_confirmed`
- `transformation_notes`

Allowed `runtime_representation_mode` values:

- `PASSIVE_ONLY` — only for `PASSIVE_KB`;
- `ORIGINAL_NATIVE` — the canonical original is itself used operationally because the target can reliably consume that format;
- `DERIVED_MIRROR` — canonical original is preserved and a separate runtime-native representation is generated.

For `OPERATIONAL_CONTROL` and `MIXED`, `PASSIVE_ONLY` is forbidden under `DUAL_RUNTIME_FIDELITY`.

## Format-specific rule

Do not convert merely because a file is not Markdown.

If a structured source format already carries execution semantics cleanly and the target can consume it reliably, prefer `ORIGINAL_NATIVE`. Examples may include JSON, YAML, XML, or plain text state/routing definitions.

If a source format is not reliably consumable as an operational instruction source at the required runtime point, preserve the original and create a `DERIVED_MIRROR`.

A DOCX containing operational instructions is therefore normally:

`canonical DOCX -> preserved original + runtime-native operational mirror`

not:

`DOCX -> replacement Markdown`

## Mixed artifacts

For `MIXED` artifacts:

1. preserve the complete original as canonical;
2. derive only the operational surface needed by the Skill;
3. keep passive Knowledge discoverable through the KB manifest;
4. record which source sections/structures feed the operational mirror;
5. never imply the operational mirror is a complete semantic replacement.

## Dependency and bootstrap preservation

Create `references/control-plane-map.json`.

It must encode the operational artifact graph and a deterministic `bootstrap_order`.

The generated `SKILL.md` must load/execute the control plane in that order before normal task execution.

Do not flatten precedence into a generic "read all files" rule when the source defines stronger ordering semantics.

## Behavioural parity

Create `references/control-plane-parity.json` with representative source-backed scenarios that exercise:

- bootstrap order;
- route/mode selection;
- at least one non-default state or branch when present;
- precedence/override behaviour;
- failure/fallback behaviour;
- output validation/contract enforcement;
- cross-layer invocation when present.

Each scenario must record `PASS`, `FAIL`, or `NOT_RUN`.

A package with `FAIL` or `NOT_RUN` control-plane parity scenarios must not be reported as behaviourally validated.

Python can enforce completeness and traceability of the record; it does not prove semantic equivalence by itself.

## Recommended layered pattern

For a layered system:

- bootstrap/orchestrator layer: preserve canonical original and ensure an operational runtime representation;
- state-machine/router layer: preserve native structured form when it is already suitable and runtime-readable;
- meta-prompt/policy/template layer: preserve canonical original and create runtime-native mirrors or focused modules when direct binary consumption is not reliable.

The exact filenames and number of layers are source-dependent. Infer roles from content and invocation relationships, not naming conventions.
