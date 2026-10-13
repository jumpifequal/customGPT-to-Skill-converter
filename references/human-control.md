# Human-in-Control Conversion Protocol

## Principle

Every CustomGPT conversion is a human-controlled migration.

The converter may detect, classify, recommend, validate, and explain. It must not silently choose a consequential migration option on behalf of the user.

A choice is consequential when it can change behaviour, fidelity, latency, runtime compatibility, persistence, retrieval, packaging, tool use, or user-visible output.

## Mandatory order for every conversion

1. Inspect the source and identify all consequential conversion parameters.
2. Present a **Decision Awareness Guide** before asking for confirmation.
3. For every parameter, explain:
   - what is being decided;
   - available options;
   - rationale for each option;
   - practical consequences/trade-offs;
   - any source/runtime evidence that makes an option more or less suitable;
   - a conservative recommendation when one is justified.
4. Ask the human to confirm the selected values.
5. Do not generate the target Skill until all applicable consequential choices are confirmed.
6. Write the selections to the deterministic decision record.
7. Generate and show the **Conversion Parameter Report**.
8. Validate the decision record and parameter report.
9. Only then proceed with target generation.

Human approval is not a ceremonial acknowledgement. The explanation must be sufficient for the user to understand what changes in the resulting Skill.

## Decision Awareness Guide format

Use one compact section per decision.

Required fields:

- **Parameter**
- **Why it matters**
- **Options**
- **Rationale**
- **Practical consequence**
- **Recommended choice** — only when supported by source/runtime evidence; otherwise state `NO DEFAULT`
- **User action required**

Do not bury consequences in technical prose.

If several parameters are independent, they may be presented in one table, but every option must still have a rationale and consequence.

## Global Human-in-Control rule

The human controls every consequential choice.

The converter may automatically derive non-consequential facts such as:
- file count;
- media type;
- SHA-256;
- detected icon dimensions;
- projected archive size;
- presence/absence of a source feature.

These must be marked `DETECTED` or `DERIVED`, not `HUMAN`.

The converter must not silently auto-select:
- control-plane strategy;
- DOCX transformation strategy;
- new harness insertion;
- conversational classification when ambiguous/conversational;
- persona-drift policy;
- host-continuity assumption;
- lossy/package-size reduction;
- externalization of Knowledge;
- destructive source replacement;
- tool/action substitutions;
- any other option that changes fidelity or behaviour.

## Batch confirmation

To reduce friction, after the Decision Awareness Guide the user may confirm all proposed selections in one explicit action, for example:

`CONFIRM ALL RECOMMENDED`

This is valid only if:
- every proposed parameter and consequence has already been shown;
- no parameter is marked `NO DEFAULT`;
- no destructive/lossy choice is included unless it received its own explicit acknowledgement.

Batch confirmation never bypasses specific acknowledgement requirements.

## Conversion Parameter Report

Every conversion must produce a Markdown table after the user confirms choices and before target generation.

Required columns:

| Parameter | Selected value | Origin | Rationale | Practical consequence |
|---|---|---|---|---|

Allowed `Origin` values:
- `HUMAN` — explicitly selected or explicitly batch-confirmed by the user;
- `SOURCE` — directly required by the source artifact/contract;
- `DETECTED` — objectively detected from source/package/runtime facts;
- `DERIVED` — deterministically calculated from confirmed inputs.

The table must include every parameter that materially influenced the conversion architecture, even when the value is `NOT_APPLICABLE`.

At minimum include, when relevant:
- Knowledge preservation mode;
- control-plane presence and strategy;
- runtime representation mode for operational artifacts;
- DOCX presence and strategy;
- conversational classification;
- persona-drift policy;
- host continuity;
- harness source presence/action/profile;
- package-size status and oversize strategy;
- icon normalization mode;
- tool/action compatibility decisions;
- destructive/lossy transformation approvals.

## Persistent evidence

Write the same report to `references/conversion-parameters.md` in the generated Skill when the target package contains conversion-decision evidence.

Store the machine-readable choices in `references/conversion-decisions.json`.

The Markdown report is user-readable evidence; the JSON record is the deterministic validation source.

## Failure semantics

Stop conversion when:
- an applicable choice has not been explained;
- rationale or consequence is missing;
- a required human choice is unconfirmed;
- a destructive/lossy acknowledgement is missing;
- the parameter report cannot be generated;
- the report and decision record disagree.

Never infer consent from silence, prior unrelated approvals, or a recommendation.
