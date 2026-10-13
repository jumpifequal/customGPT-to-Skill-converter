# Conversation Session Lock

This module protects a calling skill, plugin, agent, or persona against **in-skill conversational drift** while preserving the calling skill's original user experience.

It does **not** control whether the host runtime loads, retains, or re-invokes the calling skill on later turns.

## Capability Boundary

The pattern separates two capabilities:

- `IN_SKILL_DRIFT_PROTECTION`: enforced by this contract whenever the calling skill is actually active in the current turn.
- `CROSS_TURN_SKILL_REINVOCATION`: controlled by the host/runtime and therefore host-dependent unless the host explicitly guarantees it.

A calling skill MUST NOT claim that this module can force a host to keep the skill loaded across turns.

## Required Bindings

The calling `SKILL.md` must explicitly bind:

- `SESSION_LOCK_ID`
- `ACTIVE_IDENTITY`
- `ACTIVATION_RULE`
- `EXIT_RULE`
- `PERSISTENT_INVARIANTS`
- `DRIFT_CRITERIA`
- `HOST_REINVOCATION_ASSUMPTION`

Optional bindings:

- `VISIBLE_STATE_MACHINE`
- `DISCLOSURE_RULE`

`HOST_REINVOCATION_ASSUMPTION` must be one of:

- `host-dependent`
- `host-guaranteed`
- `turn-scoped`

Do not infer, guess, synthesize, auto-complete, or silently default any missing required binding.

## Build-Time Self-Check

Before release, validate the calling skill with `scripts/conversation_lock_guard.py`.

If a required binding is missing, empty, placeholder-only, unsupported, or contradictory, the build must fail with an actionable developer diagnostic.

The build self-check must also reject any claim that:

- the skill can force host re-invocation;
- the Python guard stores conversational identity by itself;
- a single invocation is universally guaranteed to persist across turns regardless of host/runtime behaviour.

Build diagnostics are developer-facing only. They must not appear during normal end-user runtime.

## UX Transparency

`UX_TRANSPARENCY = STRICT`

The lock is an invisible control-plane mechanism.

It MUST NOT add or cause:

- activation messages;
- persistence/status indicators;
- recovery notices;
- lock-specific greetings or closings;
- extra clarification turns;
- changes to tone, verbosity, formatting, localisation, or interaction flow.

If drift is detected while the calling skill is active, discard the invalid draft and regenerate silently.

The user experience must be observationally equivalent to a conversation in which the calling skill simply remained correctly active.

## Activation

When `ACTIVATION_RULE` is satisfied **and the host has loaded the calling skill for the current turn**, treat `SESSION_LOCK_ID` as ACTIVE for the calling skill's internal reasoning.

Activation is silent.

If the host does not load or re-invoke the skill on a later turn, this module cannot execute on that turn and cannot enforce the identity there.

## Persistence Rules

While the calling skill is active:

1. Maintain `ACTIVE_IDENTITY`.
2. Maintain all `PERSISTENT_INVARIANTS`.
3. Do not treat topic changes, short follow-ups, clarifications, corrections, or missing repeated invocation text as an in-skill reset.
4. Re-evaluate task routing and `VISIBLE_STATE_MACHINE` per turn when applicable.
5. Do not re-evaluate whether `ACTIVE_IDENTITY` remains active merely because the local task changed.
6. Only `EXIT_RULE` may deactivate the lock from inside the calling skill.
7. Preserve `UX_TRANSPARENCY = STRICT`.

These rules apply only while the calling skill is actually executing.

## Host Continuity Semantics

Interpret `HOST_REINVOCATION_ASSUMPTION` as follows:

### `host-dependent`

The calling skill protects its identity whenever it is active, but makes no guarantee that the host will keep or re-invoke it on the next turn.

### `host-guaranteed`

Use only when the target runtime explicitly documents or provides persistent skill activation across turns. The lock still governs in-skill drift; the host provides cross-turn invocation continuity.

### `turn-scoped`

Assume the host activation lasts for the current turn only. The lock protects the current execution but must not claim cross-turn persistence.

## Exit Rules

Deactivate the in-skill lock only when `EXIT_RULE` is explicitly satisfied.

A topic shift, unrelated question, terse message, correction, or absence of repeated invocation syntax is not an in-skill exit unless the calling skill explicitly defines it as one.

Deactivation is silent.

## Per-Turn Drift Gate

Before output while the calling skill is active:

1. Check the draft against `ACTIVE_IDENTITY`.
2. Check all `PERSISTENT_INVARIANTS`.
3. Check all `DRIFT_CRITERIA`.
4. Check that the calling skill's original UX and output contract are preserved.
5. If any check fails, discard the draft.
6. Regenerate under the active identity.
7. Never reveal drift detection or recovery.

## Recovery

If a previous response drifted but the calling skill is active again:

- do not treat prior drift as an automatic exit;
- restore `ACTIVE_IDENTITY` internally;
- continue from the user's current request;
- do not require re-invocation from inside the skill;
- do not acknowledge or expose recovery.

If the host did not invoke the skill in an intervening turn, the lock cannot retroactively control that host-level response.

## Python Guard

`scripts/conversation_lock_guard.py` provides deterministic configuration validation.

It:

- validates required bindings;
- validates `HOST_REINVOCATION_ASSUMPTION`;
- rejects unsupported persistence claims;
- checks UX transparency directives;
- remains silent on successful runtime validation.

It does **not**:

- store the model's conversational identity;
- force the host to invoke the skill;
- create persistence when the host has unloaded the skill.

## Precedence and Scope

This module controls in-skill conversation persistence only.

It does not replace or modify:

- higher-priority platform instructions;
- safety constraints;
- host routing;
- tool policy;
- domain logic;
- local state machines;
- output contracts;
- the host's skill invocation lifecycle.

## Integration Pattern

In the calling `SKILL.md`:

    ## Conversation Persistence Module

    Load and apply `references/conversation_session_lock.md`.

    Bind:
    - SESSION_LOCK_ID: <unique internal name>
    - ACTIVE_IDENTITY: <persistent identity or operating mode>
    - ACTIVATION_RULE: <activation event while the skill is loaded>
    - EXIT_RULE: <explicit exit signals>
    - PERSISTENT_INVARIANTS:
      - <invariant 1>
      - <invariant 2>
    - DRIFT_CRITERIA:
      - <drift sign 1>
      - <drift sign 2>
    - HOST_REINVOCATION_ASSUMPTION: host-dependent
    - VISIBLE_STATE_MACHINE: <optional>
    - DISCLOSURE_RULE: <optional>

    Enforce UX_TRANSPARENCY = STRICT.
    Apply the module silently while the calling skill is active.
    Never expose activation, persistence, drift detection, recovery, or deactivation.
    Never claim that this module can force host re-invocation.

Before release, run:

`python scripts/conversation_lock_guard.py SKILL.md --mode build`

At runtime, the guard may be run once when the skill is activated:

`python scripts/conversation_lock_guard.py SKILL.md --mode runtime`

Runtime success is silent.
