# Knowledge-Base and DOCX Migration

## Principle

Preserve source Knowledge as evidence, not merely as extracted text.

A format conversion can change semantics. This is especially important for DOCX because meaning may depend on structure or features that Markdown cannot faithfully represent, including tables, headers/footers, footnotes/endnotes, comments, tracked changes, fields, section boundaries, text boxes, embedded objects, hyperlinks/relationships, numbering, captions, alt text, and layout-dependent reading order.

Therefore, never replace a DOCX with Markdown merely for convenience unless the human explicitly approves that semantic risk.

## Preferred architecture

Use a dual-representation strategy when the target runtime benefits from text-native retrieval:

1. **Authoritative original** — preserve the original file byte-for-byte under `references/kb/original/`, retaining its relative source path when practical.
2. **Derived access mirror** — optionally create a text/Markdown/JSON extraction under `references/kb/derived/` only to improve retrieval or inspection.
3. **Provenance link** — record source path, target path, SHA-256, media type, byte size, and any derived-mirror path in `references/kb-manifest.json`.
4. **Authority rule** — the original binary remains authoritative. A derived mirror is never proof that all document semantics were preserved.
5. **Runtime rule** — when the runtime can inspect the original format directly, prefer the original for fidelity-sensitive questions; use the derived mirror for search/navigation and verify against the original when formatting, comments, fields, revisions, or structure may matter.

Do not silently flatten DOCX, PDF, PPTX, XLSX, images, archives, or other binary Knowledge formats.

## DOCX human gate

Run artifact-role classification before this gate.

For DOCX classified `PASSIVE_KB`, stop before transforming it and show this short rationale:

- `PRESERVE_ORIGINAL_ONLY` — safest for document fidelity. Keep the DOCX byte-for-byte and reference it from the Skill. Retrieval may require document-capable tooling at runtime.
- `PRESERVE_PLUS_DERIVED` — recommended general passive-KB mode. Keep the original DOCX byte-for-byte and also create a non-authoritative text-native mirror for retrieval.
- `CONVERT_AND_REPLACE` — smallest/simplest package, but potentially destructive. Only use with explicit human acceptance that DOCX-only semantics may be lost.

For DOCX classified `OPERATIONAL_CONTROL` or `MIXED`, the control-plane gate takes precedence. `PRESERVE_ORIGINAL_ONLY` must not be described as runtime-safe: preserve the canonical DOCX and create a runtime-native operational mirror unless reliable direct runtime consumption is explicitly confirmed.

Require a human choice. Do not default silently.

If `CONVERT_AND_REPLACE` is chosen for passive Knowledge, require `semantic_loss_acknowledged: true` in the deterministic decision record.

## Knowledge-base preservation

For the entire Custom GPT Knowledge Base:

- preserve every source file byte-for-byte whenever the Skill package/runtime permits it;
- keep original filenames and relative paths when safe and practical;
- never infer that a file is disposable from its extension or filename;
- generate `references/kb-manifest.json`;
- record SHA-256 for every preserved original;
- reference the KB manifest from `SKILL.md`;
- use shallow per-domain indexes only when they materially improve retrieval;
- do not replace originals with normalized derivatives unless the human explicitly authorizes that replacement.

When a target runtime cannot directly consume a source format, preserve the original anyway when size permits, add a derived access representation, and document the runtime limitation.

## Package-size gate

The installable Skill archive must remain at or below 25 MiB unless the active runtime explicitly documents another limit.

Before packaging, run the deterministic size guard.

If the projected compressed archive exceeds the limit, stop and explain:

> The package is over the 25 MiB Skill limit. Normal ZIP compression is already applied, and formats such as DOCX, PDF, PNG, JPEG, and ZIP are often internally compressed, so extra lossless compression may have limited effect. I can first apply lossless size reduction. If that is still insufficient, any stronger reduction may require changing fidelity or moving content outside the Skill.

Require one human choice:

- `LOSSLESS_FIRST` — apply only lossless package optimization. If the package still exceeds 25 MiB, stop and ask again.
- `EXTERNALIZE_WITH_REFERENCE` — move selected large Knowledge outside the Skill only when the target workflow supports reliable external access; record the dependency and preserve hashes.
- `LOSSY_WITH_APPROVAL` — allow specifically identified fidelity-reducing transformations only after explaining affected files and risks.
- `ABORT` — keep fidelity and stop packaging.

Never silently downsample, recompress, truncate, summarize, or discard Knowledge to meet the size limit.

## Deterministic decision record

Create a JSON decision record in the conversion workspace and, when human gates were used, preserve a copy as `references/conversion-decisions.json` in the generated Skill.

Validate it with `scripts/decision_gate_guard.py`.

At minimum, track:

- Knowledge preservation mode;
- control-plane presence, selected strategy, and runtime-risk acknowledgement when applicable;
- DOCX presence and selected DOCX strategy;
- semantic-loss acknowledgement when applicable;
- conversational classification and persona-drift choices when applicable;
- host continuity choice when applicable;
- projected archive size;
- oversize strategy when applicable;
- whether any lossy change was explicitly authorized;
- timestamp or run identifier when available;
- source and target inventory hashes when available.

A human gate is not complete until the deterministic record passes validation.


## Interaction with control-plane artifacts

Before applying ordinary KB handling to a source file, check its `ARTIFACT_ROLE`.

If it is `OPERATIONAL_CONTROL` or `MIXED`, `references/control-plane-migration.md` governs runtime representation first.

The original still belongs to the preservation manifest, but an operational artifact must not be treated as passive Knowledge merely because it arrived through the Custom GPT Knowledge upload mechanism.

For operational DOCX files, the conservative default is not `PRESERVE_ORIGINAL_ONLY`. Use canonical-original preservation plus a runtime-native operational mirror unless the target runtime is explicitly confirmed to consume the original DOCX reliably at the required execution point.
