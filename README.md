# CustomGPT-to-Skill

<p align="center">
  <img src="docs/assets/logo.svg" alt="CustomGPT-to-Skill logo" width="180">
</p>

<p align="center">
  <a href="#install"><img alt="Install with npx" src="https://img.shields.io/badge/install-npx%20skills%20add-CB3837"></a>
  <img alt="Skill version" src="https://img.shields.io/badge/skill-10.7.0-2F6BFF">
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-green"></a>
  <a href="README.it.md"><img alt="Italiano" src="https://img.shields.io/badge/lingua-italiano-009246"></a>
</p>

> ## Custom GPTs are being retired
>
> OpenAI has scheduled the retirement of **custom GPTs for 11 December 2026**. After that date GPTs and their GPT pages become inaccessible. Enterprise workspaces with an approved deferral have until 11 February 2027. Dates and availability can differ per account or workspace, so follow the notice in your account. [[1]](#sources)
>
> OpenAI's recommended path is a built-in **Migrate to plugin** flow. For many GPTs it is the right answer. For others a plugin is not the best target. In that case you need a **Custom GPT → Skill** conversion, and that is what this repository does.

🇮🇹 [Leggi in italiano](README.it.md)

*Facts about third-party products were checked on 13 October 2026; see [Sources](#sources).*

---

## What happens on 11 December

OpenAI's migration FAQ describes what the built-in migration does and does not do. [[1]](#sources)

| | |
|---|---|
| **Carried over** | The GPT's instructions become a skill inside the new plugin. Knowledge files are copied into the plugin's reference files. Connected apps are added to the plugin as apps. Migration uses the latest *published* version. |
| **Not carried over** | Custom actions. The selected model. Sharing settings (the plugin starts private and existing users do not get access). Existing conversations do not move to the plugin; OpenAI says they remain accessible after retirement. |
| **Also good to know** | OpenAI says a migrated plugin may respond differently, so test it. The original GPT becomes read-only after migration. Making a plugin public needs a separate submission process. Only the creator (or an Enterprise workspace admin) can migrate a GPT. |

Google is making a similar move: Gemini Gems are being replaced by Skills, and Google will start migrating them automatically on 17 November 2026. [[2]](#sources) More detail in [docs/migration-landscape.md](docs/migration-landscape.md).

## Two ways out

**1. Built-in migration to a plugin (OpenAI).** Start here when your GPT is mostly instructions plus knowledge files, you only need ChatGPT or Codex, and you can accept re-testing and re-sharing. The original stays usable until retirement (read-only once migrated).

**2. Conversion to a Skill (this repository).** Consider it when one or more of these apply:

- **You need the same package beyond ChatGPT.** `SKILL.md` is a file-based format that OpenAI's API documentation describes as compatible with the open Agent Skills standard, and Microsoft 365 Copilot declarative agents accept custom skills as a zip with `SKILL.md` (preview, Frontier program). Check each runtime's limits. [[5]](#sources) [[6]](#sources)
- **Your GPT is stateful, conversational or Socratic** and its persona must survive follow-ups. The converter detects such GPTs, asks you how to treat persona drift, and can add a host-aware session lock. It never claims it can force the host to re-invoke the skill.
- **Your GPT has a layered "control plane"** (files that decide what to load, in what order, and what wins). The converter classifies every artifact and preserves both the canonical original and a runtime-executable form.
- **You want to own and audit the result.** A skill is a folder of plain files you can keep in Git, review, hash and test. Knowledge files are preserved byte for byte with a SHA-256 manifest, and the converter ships a regression suite.

A plugin can contain skills, and a skill can be uploaded on its own. [[3]](#sources) [[4]](#sources)

## What this skill does

You give it a Custom GPT export (a ZIP, or the instructions plus Knowledge files and an optional icon). It then:

1. **Inventories** every source file with its SHA-256 and finds the real instruction source by content, not by file name.
2. **Asks you plain-language questions.** Every decision comes with its options, rationale and practical consequence. Nothing is generated until you confirm. The questions cover control-plane strategy, any validation harness, whether the GPT is conversational and how to treat persona drift, how to handle DOCX Knowledge files, and what to do if the package is too large.
3. **Implements the solutions you chose:** an instruction-preserving `SKILL.md`, byte-preserved Knowledge with a manifest, normalized icons, ChatGPT/Codex UI metadata (`agents/openai.yaml`), and only the helper files that materially help.
4. **Validates** the result with a deterministic parameter report, structural checks, a source-to-target manifest comparison and a size check, then delivers `skill.zip` and a conversion dashboard that separates validation *run* from *not run*.

The goal is **functional equivalence of instructions, knowledge and control flow**: the converted skill reproduces what your GPT was told to do, together with its Knowledge and its control files. Test it on real prompts, as you would after any migration.

### Scope and current limits

- **Custom Actions** are reported as explicit conversion gaps. A skill can bundle a script that calls the Action's API where the runtime allows network access; generating such scripts is not yet part of the converter. [[3]](#sources) [[6]](#sources)
- **Unsupported capabilities** are reported as conversion gaps. The converter works from what the source defines, so connectors, endpoints and secrets are never invented.
- **Package size:** the gate is 25 MiB compressed by default (`--limit-mib` changes it). Above it, you choose: lossless first, externalize with a reference, lossy with approval, or abort. DOCX files are kept as originals; a text mirror is an optional retrieval aid.
- **Platform features** such as GPT Store distribution, platform memory, voice and model selection belong to the platform, not to the skill package.

## Skill or plugin: trade-offs

Verified facts first, then the author's experience.

| | Plugin (OpenAI) | Skill (this converter's output) |
|---|---|---|
| What it is | Bundles skills, connected apps, app templates and extensions [[4]](#sources) | Instructions, examples and code in a folder with `SKILL.md` [[3]](#sources) |
| Custom Actions | Must be rebuilt, for example as an app or a custom MCP server [[1]](#sources) | Reported as a conversion gap; a bundled script can call the API where the runtime allows network access |
| MCP-based apps | Local MCP apps run on ChatGPT Desktop but are not available on web or mobile; other options are a workspace app or an app hosted on ChatGPT Sites [[4]](#sources) | Not required for instruction-and-knowledge skills |
| Sharing | New plugins start private; public listing needs a submission process [[1]](#sources) [[4]](#sources) | Share the package or the repository; availability depends on the product and plan [[3]](#sources) |
| Size | See the plugin documentation for current limits | Converter gate: 25 MiB compressed by default. OpenAI's Skills API documents 50 MB per zip, 25 MB per uncompressed file and 500 files; Microsoft's Agent Builder documents 50 MB per zip and up to 8 skills per agent. [[5]](#sources) [[6]](#sources) |
| Availability | Plugin access depends on plan, workspace and region [[4]](#sources) | In ChatGPT, personal skills are documented for eligible Business, Enterprise, Healthcare and Edu users, subject to workspace settings. Check your plan. [[3]](#sources) |

**Author's notes (from experience with conversational and Socratic GPTs):** converted skills run slightly slower than the original GPTs. Anyone who installs a skill can read its instructions and files, so keep secrets out of it. Distribution is less efficient than sharing a GPT link. For stateful conversational GPTs we chose skills because the semantics carry over intact.

> Skills run with the permissions of the agent that loads them. Review any skill, including conversions produced by this one, before installing it. OpenAI also scans uploaded skills and tells you to review them yourself. See [SECURITY.md](SECURITY.md). [[3]](#sources)

## Workflow

```text
Custom GPT export
  ↓
Source inventory (SHA-256)
  ↓
Human-in-Control: Decision Awareness Guide → explicit confirmation
  ↓
Control-plane · Harness · Conversational · DOCX gates
  ↓
Conversion Parameter Report (deterministic, shown to you)
  ↓
Target generation (Skill + preserved Knowledge + icons)
  ↓
Regression · structural validation · manifest comparison · size gate
  ↓
skill.zip + conversion dashboard
```

## Install

Install directly from GitHub with the open `skills` CLI:

```bash
npx skills add jumpifequal/customGPT-to-Skill-converter
```

Inspect what the CLI detects before installing:

```bash
npx skills add jumpifequal/customGPT-to-Skill-converter --list
```

Install globally for a specific agent (identifiers are listed by the CLI):

```bash
npx skills add jumpifequal/customGPT-to-Skill-converter -g -a codex -y
npx skills add jumpifequal/customGPT-to-Skill-converter -g -a claude-code -y
```

Install from a local clone:

```bash
git clone https://github.com/jumpifequal/customGPT-to-Skill-converter.git
cd customGPT-to-Skill-converter
npx skills add .
```

Verify the repository before installation or contribution:

```bash
python -m pip install -r requirements-dev.txt
python tools/validate_repo.py
```

> `npx skills add` installs the skill; the repository itself needs no `npm install`. SVG icon sources additionally need `cairosvg` (not needed for the test suite). You can also upload the skill folder as a zip wherever your product accepts skills.

## Quick start

Attach your Custom GPT export (or instructions, Knowledge files and an optional icon) and say:

```text
Use $customgpt-to-skill to convert my attached Custom GPT export into a validated Universal Skill package.
```

Typical natural triggers: *convert, port, migrate or rebuild this Custom GPT as a Skill*; *turn this GPT export into a skill*; *re-run my GPT-to-skill conversion with the new Knowledge files*.

## Worked example

*Illustrative and abbreviated: wording, files and values depend on your GPT.*

**1. Prepare the input.** Put the GPT's instructions and the Knowledge files you uploaded in one ZIP:

```text
contract-reviewer-gpt.zip
├── system_prompt.md          # the GPT's instructions
└── knowledge/
    ├── clause-playbook.docx
    ├── risk-matrix.csv
    └── glossary.md
```

**2. Invoke the skill** in a runtime where it is installed, with the ZIP attached:

```text
Use $customgpt-to-skill to convert the attached Custom GPT export (contract-reviewer-gpt.zip) into a validated Universal Skill package.
```

**3. Review the Decision Awareness Guide.** The skill inventories the four files (path, size, SHA-256), then lays out each decision with its options and consequences:

```text
Inventory: 4 files. Instructions: system_prompt.md (identified by content).
Knowledge: clause-playbook.docx, risk-matrix.csv, glossary.md.

Control plane: all three Knowledge files are PASSIVE_KB (evidence, no routing or precedence rules).
Conversational classification: NON_CONVERSATIONAL_CANDIDATE (one-shot review task, no persona persistence).
Harness: the instructions already define an output schema and fallbacks, so they are preserved (PRESERVE_EXISTING).

DOCX decision for clause-playbook.docx:
  PRESERVE_ORIGINAL_ONLY  keeps the file byte for byte; retrieval may need document tooling at runtime.
  PRESERVE_PLUS_DERIVED   (recommended) keeps the original and adds a text mirror for retrieval.
  CONVERT_AND_REPLACE     smallest package; DOCX-only semantics may be lost.

Reply CONFIRM ALL RECOMMENDED, or tell me what to change.
```

**4. Confirm.**

```text
CONFIRM ALL RECOMMENDED
```

**5. Check the Conversion Parameter Report and the dashboard.** Before generating anything, the skill shows the parameters it will use:

| Parameter | Selected value | Origin | Rationale | Practical consequence |
|---|---|---|---|---|
| DOCX files in Knowledge | 1 | DETECTED | `clause-playbook.docx` found in the source | The DOCX gate applies |
| DOCX strategy | `PRESERVE_PLUS_DERIVED` | HUMAN | Keep fidelity and give the runtime a searchable text mirror | Original kept byte for byte; the mirror is an access aid |
| Projected package size | under 25 MiB | DERIVED | Compressed size measured by the size guard | No size-reduction decision needed |

It then delivers `skill.zip` and a conversion dashboard: source versus target file counts, Knowledge preservation mode and manifest status, validations run and not run, unsupported capabilities listed as conversion gaps (for example custom actions), and residual risks.

**6. Install and test.** Upload `skill.zip` where your product accepts skills (in ChatGPT: Skills → Create → Upload from your computer, subject to plan and workspace settings [[3]](#sources)). Then run the prompts you normally use with your GPT and compare the answers with the original, as OpenAI also recommends after a plugin migration. [[1]](#sources)

## Helper modules

| Script | Purpose |
|---|---|
| `build_inventory.py` | Deterministic source and target inventory with hashes |
| `kb_preserve.py` | Byte-for-byte Knowledge migration and manifest |
| `icon_convert.py` | Safe PNG/SVG icon normalization |
| `detect_conversational_gpt.py` | Advisory conversational classification |
| `harness_profile_selector.py` | Advisory harness-family recommendation |
| `decision_gate_guard.py` | Validates all human gates |
| `render_parameter_report.py` | Renders and validates the Conversion Parameter Report |
| `control_plane_guard.py` | Validates control-plane map and parity |
| `conversation_lock_guard.py` | Validates conversation-lock integrations |
| `package_size_guard.py` | Projected compressed size against the limit (default 25 MiB) |
| `validate_converted_skill.py` | Structural and semantic validation of a generated skill |
| `regression_self_test.py` | Converter self-regression (F001–F031) |

## Repository structure

```text
customGPT-to-Skill-converter/
├── .github/
│   └── workflows/
│       └── validate.yml
├── agents/
│   └── openai.yaml
├── assets/
│   ├── icon.png          # skill UI icon (64×64)
│   └── icon.svg
├── docs/
│   ├── assets/
│   │   ├── logo.png      # repository logo
│   │   └── logo.svg
│   ├── architecture.md
│   ├── decision-gates.md
│   ├── examples.md
│   ├── migration-landscape.md
│   └── runtime-tools.md
├── references/           # normative conversion policies
├── scripts/              # deterministic helpers and regression suite
├── tools/
│   └── validate_repo.py
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── README.it.md
├── SECURITY.md
├── SKILL.md              # entry point
└── requirements-dev.txt
```

## Documentation

- [Migration landscape (sourced, dated)](docs/migration-landscape.md)
- [Architecture](docs/architecture.md)
- [Decision gates](docs/decision-gates.md)
- [Runtime tools](docs/runtime-tools.md)
- [Usage examples](docs/examples.md)
- [Changelog](CHANGELOG.md)

## Design constraints

The skill deliberately prefers:

- a human decision over a silent default;
- preserved originals over convenient conversions;
- explicit conversion gaps over invented capabilities;
- invariant-driven regression over schema-only validity;
- "validation not run" over an unverifiable "validated".

## Version

Skill `10.7.0`, see [CHANGELOG.md](CHANGELOG.md).

Author: **Enrico Frumento**

## License

MIT. See [LICENSE](LICENSE).

## Sources

Checked on 13 October 2026.

1. OpenAI Help Center, [Custom GPT retirement and migration FAQ](https://help.openai.com/en/articles/20001519-custom-gpt-retirement-and-migration-faq).
2. TechCrunch, [Google is killing off Gemini's Gems in favor of 'skills'](https://techcrunch.com/2026/09/28/google-is-killing-off-geminis-gems-in-favor-of-skills/), 28 September 2026.
3. OpenAI Help Center, [Skills in ChatGPT](https://help.openai.com/en/articles/20001066-skills-in-chatgpt).
4. OpenAI Help Center, [Plugins in ChatGPT](https://help.openai.com/en/articles/20001256-plugins-in-chatgpt).
5. Microsoft Learn, [Add custom skills to your declarative agent in Agent Builder (preview)](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/agent-builder-add-skills).
6. OpenAI Developers, [Skills (API guide)](https://developers.openai.com/api/docs/guides/tools-skills).
