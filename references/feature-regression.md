# Feature Regression Ledger

This ledger is normative for feature evolution. Update it before shipping any material feature change.

| ID | Feature invariant | Automated check | Failure means |
|---|---|---|---|
| F001 | SKILL.md has valid name/description frontmatter | regression_self_test.py | Converter package invalid |
| F002 | Full-skill-read and anti-shortcut controls remain present | regression_self_test.py | Partial-context execution risk |
| F003 | Source inventory is hash-based and recursive | build_inventory.py self-test | Silent source omissions possible |
| F004 | Knowledge preservation is default; unexplained source/target loss fails | validate_converted_skill.py | Behavioral/data regression |
| F005 | icon.png is physically 64×64 and icon.svg is self-contained | icon_convert.py + validator | UI icon regression |
| F006 | agents/openai.yaml icon paths resolve | validate_converted_skill.py | Broken UI metadata |
| F007 | New Python helpers contain required module header semantics | validate_converted_skill.py | Coding-discipline regression |
| F008 | Package excludes caches, bytecode, temp files, venvs | validator + self-test | Dirty package |
| F009 | Existing compatible code is not rewritten merely for style | semantic review requirement | Unauthorized code delta |
| F010 | Tool/action gaps are surfaced rather than invented | semantic review requirement | False capability claim |
| F011 | Validation claims distinguish run vs not run | SKILL.md contract | Unverifiable delivery |
| F012 | Representative target validation is run after feature evolution | regression_self_test.py guidance | Evolutionary regression risk |
| F013 | Conversational/ambiguous source classification blocks target generation until human confirmation | regression_self_test.py + semantic review | Human-in-the-loop regression |
| F014 | Approved conversational targets preserve host/skill trust boundary and use validated session-lock bindings | conversation_lock_guard.py + validator | Persona-persistence overclaim or incomplete lock |
| F015 | Persona-drift policy is explicit and never inferred from classifier output | SKILL.md + conversational-gpt-detection.md | Unapproved persona locking |
| F016 | Human conversational gate explains the practical consequence of every offered choice before collecting the compact reply | regression_self_test.py + conversational-gpt-detection.md | Uninformed human approval |
| F017 | Non-square icons are cover-reframed into 64×64 without letterbox/pillarbox bands | icon_convert.py + regression_self_test.py | Icon framing regression |
| F018 | Knowledge originals are preserved byte-for-byte with a hash-addressed KB manifest | kb_preserve.py + validator + regression_self_test.py | Knowledge fidelity regression |
| F019 | DOCX transformation never proceeds without a human fidelity decision and semantic-loss acknowledgement when replacing originals | decision_gate_guard.py + semantic review | Silent document-semantic loss |
| F020 | Projected compressed package size is checked before release and oversize reduction is human-gated | package_size_guard.py + decision_gate_guard.py | Invalid or silently degraded package |
| F021 | Applicable human gates are deterministically recorded and validated before progression | decision_gate_guard.py + regression_self_test.py | Untraceable or bypassed human decision |
| F022 | Every source artifact is classified as passive KB, operational control, or mixed before runtime architecture is finalized | control-plane policy + decision record | Control files misclassified as passive Knowledge |
| F023 | Operational/mixed artifacts preserve canonical originals and have an explicit runtime representation mode | control_plane_guard.py + validator | Byte fidelity without runtime executability, or untraceable transformation |
| F024 | Source bootstrap/dependency order is represented and validated for operational artifacts | control_plane_guard.py | Precedence/routing drift |
| F025 | Control-plane parity scenarios must be executed and PASS before behavioural validation can be claimed | control_plane_guard.py + regression_self_test.py | False behavioural-equivalence claim |
| F026 | Existing source harness controls are preserved before any reusable template is considered | harness policy + semantic review | Source behaviour weakened by template replacement |
| F027 | New harness insertion is human-gated and deterministically recorded | decision_gate_guard.py + regression_self_test.py | Unapproved behavioural change |
| F028 | Harness family selection is advisory, task-family-specific, and never injects the full library into one target | harness_profile_selector.py + regression_self_test.py | Over-broad or self-authorized harness |
| F029 | Every conversion explains consequential choices with rationale and practical consequences before asking for confirmation | human-control policy + regression_self_test.py | Uninformed or ceremonial consent |
| F030 | Every conversion requires explicit global human confirmation before target generation | decision_gate_guard.py + regression_self_test.py | Silent/default migration choice |
| F031 | Every conversion emits a deterministic parameter table with selected value, origin, rationale, and practical consequence | render_parameter_report.py + validator + regression_self_test.py | Untraceable conversion configuration |

## Evolution protocol
1. Add or modify the smallest feature surface.
2. Add/update its invariant in this ledger.
3. Run the narrowest relevant check.
4. If it fails, repair only the failing feature surface.
5. Rerun the narrow check.
6. Run the full regression suite.
7. Validate at least one representative generated target package.
8. Reject the release if any previously passing invariant fails.

## Backward-compatibility rule
Feature additions must not weaken source preservation, Knowledge byte fidelity, DOCX authority rules, Human-in-Control rationale/confirmation, parameter-report traceability, decision-gate traceability, package-size gating, icon validity, metadata path integrity, package hygiene, coding discipline, human confirmation for conversational classification, host-continuity boundaries, or evidence-backed validation.

## Clean-room generated Skill invariant

The installed Skill starts from its present operational instructions and visible user input. Conversion decisions, historical reports, provenance audit files, GPT-origin claims, and implied prior chat memory must not be embedded in generated operational instructions or release ZIP. Preserve canonical source Knowledge byte-for-byte, even if it contains historical wording; keep conversion evidence separately in the conversion workspace. The package validator must reject generated conversion-only artifacts and conversion-history claims in SKILL.md or agents/openai.yaml.
