---
name: product-hypothesis
description: >-
  Work through a large product hypothesis with Ivan Zamesin's Next Move Theory
  (Advanced Jobs To Be Done) instead of generic JTBD. Use when the user wants to
  decide what to build, who for, how to position, whether a bet should live,
  diagnose a live product, size a market, craft a value proposition, write a
  strategy PRD, plan go-to-market, or analyze customer interviews. Triggers:
  product hypothesis, крупная продуктовая гипотеза, JTBD, Jobs to be Done,
  segmentation, value proposition, PMF, positioning, should we build, market
  research, RAT, riskiest assumption, diagnose the product, go-to-market.
  Do not use for factory tickets, bugfixes, or implementing an already-approved spec.
---

# Product hypothesis — Next Move Theory front door (Cursor)

A Cursor router for **large product bets**. It does not invent methodology. It classifies the request, loads the matching Next Move Theory skill from `.cursor/skills/`, and reads the canon at `Next-Move-Theory-Canon/` before answering.

Upstream of AI-Factory. Output is a **hypothesis with a cheapest test**, not a ticket to implement.

> **Canon + skills** are Ivan Zamesin's public Next Move Theory bundle (CC BY-NC-SA 4.0). Source: https://github.com/zamesin/Next-Move-Theory-Canon-and-Skills — installed version in `.nmt-version`. How this repo wires them: `process/next-move-theory/README.md`.

---

## Cursor runtime (read this before the NMT skill)

The vendored `nmt-*` skills were written for Claude Code and Codex. In Cursor:

1. **Read** `.cursor/skills/<skill>/SKILL.md` (and `references/` plus `../PRODUCER-CONTRACT.md` / `../READABILITY-CONTRACT.md` when that skill says so). Then follow it.
2. **Ask questions in chat.** Do not call `AskUserQuestion` or `request_user_input` — those tools are not available here. One or two focused questions; wait for the reply.
3. **Tools:** `Read`, `WebSearch`, `WebFetch`, `Task` (subagents for Deep mode), `Write`. If a skill names a Claude/Codex-only tool, use the Cursor equivalent.
4. **Canon path:** `Next-Move-Theory-Canon/…` at the repo root. If a file is missing, say so; do not fill gaps with generic JTBD from training data.
5. **Default artifact path for this repo:** `apps/zarya-tg/docs/research/nmt/` (Markdown). Do not write to `Skills-Results/` unless the user asks. One file per run.
6. **Do not implement** product code, tickets, or ADRs in the same pass unless the user explicitly asks to turn a *validated* decision into factory artifacts. Even then: spec/ADR first, no silent MVP expansion.

---

## Step 0 — is this a large hypothesis?

**Large (use this skill + NMT):**

- New or shifted **segment + Job** (who we compete for, and which Core Jobs)
- New **value proposition**, positioning, or go-to-market
- "Should we build X?" where X changes the product's Job Graph, not just a screen
- Live-product diagnosis: metric drop, PMF doubt, growth, what to do next strategically
- Customer interviews to reconstruct Jobs
- A bet that would need a **new ADR** because it changes strategy or who the product is for

**Small (do not run the NMT pipeline):**

- Factory-queued tickets with an approved Human summary
- Bugfixes, copy, layout, refactors
- Implementing an already-approved spec/ADR
- A local feature that does not change Segment+Job — still needs the existing spec/ticket process, not this pipeline

If classification is unclear, treat it as large for **one** advisory turn (facts vs assumptions + the single riskiest assumption), then stop and ask whether to run a producer skill.

---

## Step 1 — route

Read the matching skill, then the canon files it lists as mandatory:

| Situation | Skill to read |
|---|---|
| Unsure / messy notes / "help me think" | `.cursor/skills/nmt-chat/SKILL.md` |
| Live product: risks, growth, "what next" | `.cursor/skills/nmt-diagnose/SKILL.md` |
| New idea: which segment + Jobs first | `.cursor/skills/nmt-market-research/SKILL.md` |
| Have interviews / calls / open-ends | `.cursor/skills/nmt-analyze-interviews/SKILL.md` |
| Segment + Jobs chosen; need value | `.cursor/skills/nmt-craft-value-proposition/SKILL.md` |
| Value chosen; need build spec | `.cursor/skills/nmt-product-requirements/SKILL.md` |
| Value chosen; need landing / ads / growth copy | `.cursor/skills/nmt-craft-go-to-market/SKILL.md` |
| Update the vendored canon + skills | `.cursor/skills/nmt-upgrade/SKILL.md` then `process/next-move-theory/sync-cursor-skills.sh` |

Producer pipeline (jump in where the user already is):

`nmt-market-research` → `nmt-craft-value-proposition` → `nmt-product-requirements` and/or `nmt-craft-go-to-market`

---

## Step 2 — non-negotiables (AJTBD, not generic JTBD)

These are restated from the injected Next Move Theory block in `AGENTS.md`. If unsure, **open the canon file** named in that routing table.

- A **Job** is a desired transition (situation → expected outcome), not "progress," not a persona, not a feature. Primary element: `I want to + verb`. One verb per Job.
- **Value** is greater energy efficiency for that Job vs the brain's prediction. Success criteria specify value. Feature ≠ value.
- **Segment** = similar Core Jobs + similar success criteria. Do not cut first by demographics / ICP / persona.
- Treat the idea as a stack of **risky assumptions**. Rank with RAT. Name the single riskiest assumption and the cheapest falsifying test **before** recommending a build.
- Skills produce **hypotheses, not conclusions.** LLM numbers are estimates with a verification path. Killing an idea cheaply is a successful RAT run.
- Subtract before add. Diagnosis before solutions. Frame the choice as **which Jobs of which segment**.

Do not import Christensen / Ulwick / Moesta definitions.

---

## Step 3 — zarya / AI-Factory handoff

This repo already has a build factory. NMT sits **before** it.

1. Save the run under `apps/zarya-tg/docs/research/nmt/` with a dated filename. Label every load-bearing claim `I know` / `I assume` / `I don't know`.
2. The next field move is evidence (interviews, concierge, probe), not a pull request.
3. Only after a human accepts the direction: write a spec from `process/ai-factory/SPEC_TEMPLATE.md` (Human summary first). If the change leaves current MVP scope in `apps/zarya-tg/docs/prd.md`, draft an ADR under `apps/zarya-tg/docs/decisions/` — do not implement in the same session.
4. Do not enqueue factory tickets until Definition of Ready is met.
5. User-facing product copy stays **Russian**. Research artifacts and this skill's methodology terms stay **English** unless the user asks otherwise.

---

## Anti-patterns to refuse

- Answering from training-data JTBD instead of the canon
- Jumping from a feature idea to tickets/code (`feature → interview → value-check`)
- Treating a landing page, deck, or the PRD as proof of the customer's Job
- Expanding zarya MVP in code because an NMT report sounded convincing
- Running all four producer skills unprompted when `nmt-chat` or `nmt-diagnose` is enough
