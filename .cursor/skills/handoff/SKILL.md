---
name: handoff
description: >-
  Compact the current conversation into a handoff document so another agent can
  continue. Use when the user asks for a handoff, session summary for a fresh
  agent, or multi-session continuation. Prefer this over inventing a new format.
disable-model-invocation: true
argument-hint: "What will the next session be used for?"
---

# Handoff (zarya-adapted)

Adapted from [mattpocock/skills](https://github.com/mattpocock/skills) `productivity/handoff` (MIT). Complements `.cursor/rules/handoff-summary.mdc`.

## Output path

Write the handoff under:

`apps/zarya-tg/docs/handoffs/YYYY-MM-DD-<slug>.md`

Create `apps/zarya-tg/docs/handoffs/` if missing. Use today's date and a short kebab-case slug from the next-session focus. Report the path when done.

Do **not** write to the OS temporary directory.

## Contents

Summarise the current conversation so a fresh agent can continue. Include:

1. **Goal** — what the next session should achieve
2. **Done** — what has already been completed (pointers, not paste)
3. **Decisions** — settled choices
4. **Risks / blockers** — open risks
5. **Next steps** — one to three concrete steps with key file paths
6. **Suggested skills** — which `.cursor/skills/*/SKILL.md` the next agent should read (e.g. `product-hypothesis`, `grilling`, `writing-for-agents`)

If the user passed arguments, treat them as the next-session focus and tailor the doc accordingly.

## Do not duplicate

Do not copy content already captured in other artifacts. Reference by path or URL instead:

- Specs: `apps/zarya-tg/docs/specs/`
- Tickets: `apps/zarya-tg/docs/tickets/`
- ADRs: `apps/zarya-tg/docs/decisions/`
- PRD: `apps/zarya-tg/docs/prd.md`
- NMT research: `apps/zarya-tg/docs/research/nmt/`
- Commits / PRs / diffs — link or cite SHAs

## Safety

Redact secrets: API keys, passwords, tokens, `.env` values, and personally identifiable information.
