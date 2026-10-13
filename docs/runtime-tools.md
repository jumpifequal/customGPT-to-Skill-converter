# Runtime Tools

The skill is model-driven. Deterministic helpers exist where repeatability matters. None of them performs network access.

| Script | Purpose |
|---|---|
| `build_inventory.py` | Recursive source/target inventory with size, SHA-256 and media type; detects silent file loss |
| `kb_preserve.py` | Byte-for-byte Knowledge copy under `references/kb/original/` plus `kb-manifest.json` |
| `icon_convert.py` | Normalise a PNG/JPEG/WEBP/SVG icon into a 64×64 `icon.png` and a self-contained `icon.svg` (SVG sources need `cairosvg`) |
| `detect_conversational_gpt.py` | Advisory conversational-candidate classification (never bypasses the human gate) |
| `harness_profile_selector.py` | Advisory task-family harness recommendation (never self-authorising) |
| `decision_gate_guard.py` | Validates every applicable human gate in the decision record |
| `render_parameter_report.py` | Renders/checks the mandatory Conversion Parameter Report |
| `control_plane_guard.py` | Validates control-plane roles, canonical originals, bootstrap order and parity |
| `conversation_lock_guard.py` | Validates an approved Conversation Session Lock integration |
| `package_size_guard.py` | Projected compressed size vs. the 25 MiB default limit |
| `validate_converted_skill.py` | Structural and semantic checks of a generated skill |
| `regression_self_test.py` | Converter self-debugging against the F001–F031 invariants |

Run any helper with `--help`, or read the module docstring: each states purpose, when used, inputs, outputs and failure semantics.

## Tool-use truthfulness

Never treat `READ == EXECUTED` or `VALIDATED == RUN`. Delivery reports must separate validation actually run from validation not run.
