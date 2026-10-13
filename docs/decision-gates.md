# Decision Gates (Human-in-Control)

The converter may detect, classify, recommend, validate and explain. It must **not** silently choose a consequential migration option.

A choice is consequential when it can change behaviour, fidelity, latency, runtime compatibility, persistence, retrieval, packaging, tool use or user-visible output.

## Mandatory order for every conversion

1. Inspect the source and identify all consequential parameters.
2. Present the **Decision Awareness Guide** (parameter · why it matters · options · rationale · practical consequence · recommendation or `NO DEFAULT` · user action).
3. Collect explicit confirmation. Silence is never consent. `CONFIRM ALL RECOMMENDED` is allowed only after every option has been explained and only when no `NO DEFAULT`, destructive or lossy choice remains.
4. Write the deterministic decision record (`references/conversion-decisions.json`).
5. Render and show the **Conversion Parameter Report** (`scripts/render_parameter_report.py`).
6. Validate record and report, then — and only then — generate the target.

## Gates

| Gate | Triggered when | Options |
|---|---|---|
| Global Human-in-Control | every conversion | explicit confirmation of all parameters |
| Control plane | any `OPERATIONAL_CONTROL` / `MIXED` artifact | `DUAL_RUNTIME_FIDELITY` · `ORIGINAL_ONLY_RUNTIME_RISK` · `CUSTOM_CONTROL_PLANE` |
| Harness | no equivalent controls in the source but a useful profile is detected | `ADD_RECOMMENDED` · `NONE` · `CUSTOM` |
| Conversational | `CONVERSATIONAL_CANDIDATE` or `AMBIGUOUS` | `YES` / `NO` / `MIXED` + persona-drift policy |
| Persona drift | conversational or mixed | `STRICT_LOCK` · `BOUNDED_LOCK` · `NO_LOCK` · `CUSTOM` |
| Host continuity | a lock mode is chosen | `host-dependent` · `host-guaranteed` · `turn-scoped` |
| DOCX fidelity | any DOCX Knowledge file | `PRESERVE_ORIGINAL_ONLY` · `PRESERVE_PLUS_DERIVED` · `CONVERT_AND_REPLACE` (needs semantic-loss acknowledgement) |
| Package size | projected compressed archive > 25 MiB | `LOSSLESS_FIRST` · `EXTERNALIZE_WITH_REFERENCE` · `LOSSY_WITH_APPROVAL` · `ABORT` |

## Parameter report columns

`Parameter` · `Selected value` · `Origin` · `Rationale` · `Practical consequence`

Allowed origins: `HUMAN`, `SOURCE`, `DETECTED`, `DERIVED`. Facts the converter can compute (file count, SHA-256, icon size, projected size) are `DETECTED`/`DERIVED`, never `HUMAN`.

Canonical definitions: `references/human-control.md`, `SKILL.md`.
