# Migration landscape

Sourced facts about where each vendor is sending custom-assistant users. **Checked on 13 October 2026.** Each fact links to its source.

## OpenAI: Custom GPTs → plugins

| Fact | Source |
|---|---|
| Custom GPTs are scheduled to retire on 11 December 2026; Enterprise workspaces with a qualified, approved deferral retire on 11 February 2027. Timing and migration availability can differ per account or workspace. | [Custom GPT retirement and migration FAQ](https://help.openai.com/en/articles/20001519-custom-gpt-retirement-and-migration-faq) |
| At retirement, GPTs and their GPT pages become inaccessible. Existing conversations remain accessible. | same |
| Built-in flow: **My GPTs → Migrate to plugin**. It uses the latest published version. Instructions become a skill; Knowledge files are copied into plugin reference files; connected apps are added as apps. | same |
| Not transferred: custom actions, selected model, sharing settings. The plugin starts private; public listing needs a separate submission. The original GPT becomes read-only. OpenAI warns the plugin may respond differently. | same |
| A plugin can include skills, connected apps, app templates and extensions. Local MCP apps run on ChatGPT Desktop and are not available on web or mobile. | [Plugins in ChatGPT](https://help.openai.com/en/articles/20001256-plugins-in-chatgpt) |
| Skills can include instructions, examples and code. Personal skills are documented for eligible Business, Enterprise, Healthcare and Edu users, subject to workspace settings. Uploaded skills are scanned and should still be reviewed by you. | [Skills in ChatGPT](https://help.openai.com/en/articles/20001066-skills-in-chatgpt) |
| Skills API limits: 50 MB zip, 500 files per skill version, 25 MB per uncompressed file. The docs warn to review networking risks when skills are used with network access. | [Skills (API guide)](https://developers.openai.com/api/docs/guides/tools-skills) |

## Google: Gemini Gems → Skills

| Fact | Source |
|---|---|
| Google announced that Gems will become skills starting 17 November 2026, with automatic migration; Gems stay usable until then. | [TechCrunch, 28 Sep 2026](https://techcrunch.com/2026/09/28/google-is-killing-off-geminis-gems-in-favor-of-skills/) |

## Microsoft: Microsoft 365 Copilot declarative agents

Microsoft 365 Copilot declarative agents support custom skills.

| Fact | Source |
|---|---|
| Custom skills for declarative agents are in preview for organizations in the Microsoft Frontier program. A skill is a directory with `SKILL.md`; instructions must be under 20,000 characters. | [Custom skills in declarative agents (preview)](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/declarative-agent-skills) |
| Agent Builder: up to 8 skills per agent, each a zip of up to 50 MB. | [Add custom skills in Agent Builder (preview)](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/agent-builder-add-skills) |

## What this means for this converter

- The converter's output is a skill package in the `SKILL.md` format with ChatGPT/Codex UI metadata. Whether a given product accepts it, and under which plan, depends on that product's own skill support and limits.
- Its default package gate is 25 MiB compressed (`package_size_guard.py --limit-mib` changes it). Several documented platform limits are higher (see above), but the converter stays conservative unless you decide otherwise at the size gate.
- Custom Actions are reported as conversion gaps.
