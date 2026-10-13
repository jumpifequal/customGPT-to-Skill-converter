# Conversational GPT Detection and Human Approval

Use this reference only during CustomGPT-to-Skill conversion.

## Classification goal

Determine whether the source GPT is materially conversational before target generation.

Classify as one of:
- `CONVERSATIONAL_CANDIDATE`
- `NON_CONVERSATIONAL_CANDIDATE`
- `AMBIGUOUS`

A conversational candidate usually has at least two strong signals, or one explicit persistence signal:

- a named persona/identity expected to remain stable across turns;
- explicit multi-turn dialogue or follow-up behaviour;
- instructions that topic shifts, terse follow-ups, corrections, or clarifications must preserve the same identity;
- session/state/routing semantics that continue across turns;
- an explicit exit/reset/deactivation rule;
- persona-specific tone, interaction style, or response discipline that is expected to persist rather than apply to one isolated output;
- recovery or anti-drift requirements;
- a visible state machine whose states can change while a higher-level identity remains active.

Weak signals that are not sufficient by themselves:
- conversation starters;
- a generic "act as an expert" role;
- friendly tone;
- a one-shot content generator that happens to use first-person language;
- tool usage without conversational continuity.

Classify `AMBIGUOUS` when strong and weak signals conflict or when the source instructions do not establish whether the persona is meant to persist across turns.

## Mandatory human gate

If the analysis returns `CONVERSATIONAL_CANDIDATE` or `AMBIGUOUS`, stop conversion before generating or modifying the target Skill.

Before requesting the final compact answer, explain the choices briefly so the human understands the behavioural consequences.

### Choice guide

**Conversational classification**
- `YES` — Treat the GPT as genuinely conversational. Multi-turn identity/persistence requirements become part of the conversion and the persona-drift decision below applies.
- `NO` — Treat it as non-conversational. Do not add conversational identity-locking merely because the source uses a role, friendly tone, or conversation starters.
- `MIXED` — Treat only part of the GPT as conversational. Protect the approved conversational surface while leaving one-shot, tool, extraction, or other independent modes outside the lock.

**Persona drift**
- `STRICT_LOCK` — Strongest identity preservation while the Skill is active. Keep the approved persona and all approved persistent invariants stable across topic shifts, terse follow-ups, clarifications, and corrections; only the explicit exit rule releases them.
- `BOUNDED_LOCK` — Preserve only named identity/invariant elements. Allow normal changes in task, topic, tone, or style outside those protected elements; use this when full persona freezing would be too rigid.
- `NO_LOCK` — Add no persona-drift protection. The converted Skill may still behave conversationally, but no dedicated mechanism will detect or silently repair persona drift.
- `CUSTOM` — Define a bespoke contract. The human must specify the exact persistent invariants, drift criteria, exit rule, and any disclosure constraints before conversion continues.

**Host continuity**
- `host-dependent` — Safest default when the runtime may or may not re-invoke the Skill on later turns. The lock works whenever the Skill is active but makes no cross-turn loading guarantee.
- `host-guaranteed` — Use only when the target runtime genuinely guarantees persistent activation/re-invocation across turns. This enables end-to-end continuity when combined with the in-Skill lock.
- `turn-scoped` — Assume activation lasts only for the current turn. Protect the current execution only and make no claim of cross-turn persistence.

### Human reply format

After showing the guide, ask the human to reply in exactly one line:

`Conversational classification: YES|NO|MIXED; Persona drift: STRICT_LOCK|BOUNDED_LOCK|NO_LOCK|CUSTOM; Host continuity: host-dependent|host-guaranteed|turn-scoped`

Do not proceed until the human answers the gate.

If the human answers `NO`, continue as non-conversational and do not add the lock module.
If the human answers `MIXED`, apply drift protection only to the approved conversational surface; do not lock unrelated one-shot/tool modes.
If the human selects `CUSTOM`, require the missing custom bindings before target generation.
If the human selects `host-guaranteed`, require explicit confirmation that the target runtime really provides persistent activation; otherwise ask the human to choose `host-dependent` or `turn-scoped`.

## Integration after approval

When a lock mode is approved:

1. Load `references/conversation_session_lock.md`.
2. Derive a concrete `SESSION_LOCK_ID` from the target Skill name.
3. Bind `ACTIVE_IDENTITY` to the source identity/operating mode confirmed by the human.
4. Bind `ACTIVATION_RULE` to invocation/loading of the generated Skill in the current turn.
5. Bind an explicit `EXIT_RULE` from source semantics or human confirmation.
6. Bind `PERSISTENT_INVARIANTS` only from source-backed behaviour plus human-approved additions.
7. Bind `DRIFT_CRITERIA` as observable violations of those invariants and output contracts.
8. Bind the human-selected `HOST_REINVOCATION_ASSUMPTION`.
9. Preserve any local visible state machine independently from the session lock.
10. Enforce `UX_TRANSPARENCY = STRICT`.
11. Keep activation, drift detection, recovery, and deactivation invisible during normal runtime.
12. Never claim that the Skill or Python guard can force host-level re-invocation.
13. Include `scripts/conversation_lock_guard.py` in the generated target.
14. Run the guard in build mode against the generated `SKILL.md`; a non-zero result blocks release.
15. Runtime validation may run once at activation; success must remain silent.

## Persona-drift adaptation rules

`STRICT_LOCK`:
- preserve the complete approved persistent identity contract;
- do not treat topic shifts, short follow-ups, clarification, or correction as an internal reset;
- only the explicit exit rule may deactivate the in-skill lock.

`BOUNDED_LOCK`:
- protect only named invariants;
- allow other tone/task/style variables to change normally;
- drift checks must not over-freeze the assistant into a single response style.

`NO_LOCK`:
- omit the lock reference and guard from the generated target unless required for another approved purpose;
- state in the conversion dashboard that persona drift was consciously left unmanaged.

`CUSTOM`:
- require complete concrete bindings before generation;
- reject placeholders or missing required bindings.

## Release tests for conversational targets

A conversational target using the lock must pass:
- topic-shift continuity while the Skill remains active;
- terse follow-up continuity while active;
- silent rejection/regeneration of a deliberately generic drifted draft;
- explicit exit deactivation;
- build failure for a missing host-continuity binding;
- build failure for unsupported persistence claims;
- successful silent runtime guard validation;
- host-not-reinvoked scenario documented as outside the lock's control.
