# Matt Pocock productivity skills (vendored for zarya)

Selective adapt of [mattpocock/skills](https://github.com/mattpocock/skills) `skills/productivity` (MIT License, Copyright (c) 2026 Matt Pocock).

Installed under `.cursor/skills/` with zarya-specific gates (AI-Factory DoR, NMT routing, repo output paths). Not a full `npx skills add` of the bucket.

## Adopted

| Skill | Path | Notes |
|-------|------|--------|
| `grill-me` | `.cursor/skills/grill-me/` | User-invoked wrapper → `grilling` |
| `grilling` | `.cursor/skills/grilling/` | Pre-DoR design tree; blocked on factory / NMT / bugfix |
| `handoff` | `.cursor/skills/handoff/` | Writes to `apps/zarya-tg/docs/handoffs/` |
| `writing-for-agents` | `.cursor/skills/writing-for-agents/` | Reference when editing skills / AGENTS.md / CLAUDE.md |
| `to-questionnaire` | `.cursor/skills/to-questionnaire/` | Writes to `apps/zarya-tg/docs/questionnaires/` |

## Skipped (on purpose)

| Skill | Why |
|-------|-----|
| `teach` | Personal teaching workspace (`MISSION.md`, HTML lessons). Not part of MVP / AI-Factory. |
| `wait-what` | Depends on `CONTEXT.md` / `CONTEXT-MAP.md`, which this repo does not have (vocabulary lives in PRD, ADRs, AGENTS.md). Revisit only if a shared domain glossary is introduced. |

## Optional follow-up (not in this drop)

Matt's `skills/engineering/` bucket (`grill-with-docs`, `to-spec`, `to-tickets`, `implement`) overlaps AI-Factory templates more closely than productivity. Evaluate in a separate pass against `process/ai-factory/`.

## Upstream

- Source: https://github.com/mattpocock/skills/tree/main/skills/productivity
- License: MIT (see upstream LICENSE)
