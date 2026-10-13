# Usage Examples

These examples show invocation patterns only. They are not conversion outputs.

## Basic conversion

```text
Use $customgpt-to-skill to convert my attached Custom GPT export into a validated Universal Skill package.
```

Expected behaviour: inventory every asset → show the Decision Awareness Guide → wait for confirmation → generate → validate → deliver `skill.zip` plus the conversion dashboard.

## Instructions + Knowledge, no export ZIP

```text
Convert this GPT to a skill. Instructions are in the attached .txt, Knowledge files are the 9 JSON files, icon attached.
```

The canonical instruction source is identified by content, not by filename.

## Re-conversion with regression safety

```text
Rebuild my previous GPT-to-skill conversion. The GPT now has two more Knowledge files and a new icon.
```

A missing numbered file is never assumed intentional; the source-to-target manifest comparison fails on unexplained omissions.

## Conversational GPT

If the GPT keeps a persona across turns, generation pauses and asks for: classification (`YES`/`NO`/`MIXED`), persona-drift policy, and host-continuity assumption — each explained first.

## DOCX Knowledge

Any DOCX in Knowledge triggers the fidelity gate. The original stays authoritative; Markdown mirrors are retrieval aids only.
