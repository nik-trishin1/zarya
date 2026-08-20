---
name: grilling
description: >-
  Grill the user about a plan, decision, or design until the design tree is
  resolved. Use when the user asks to grill, stress-test a plan, or resolve
  open design branches before a spec/ticket. Never use for factory-queued DoR
  tickets, implementing an approved Human summary, bugfixes, or large product
  bets (route those to product-hypothesis / NMT).
---

# Grilling (zarya-adapted)

Adapted from [mattpocock/skills](https://github.com/mattpocock/skills) `productivity/grilling` (MIT).

## Hard exclusions (do not grill)

Stop and refuse this skill when any of the following is true:

1. The work is a **factory-queued** ticket that meets `process/ai-factory/DEFINITION_OF_READY.md` (approved Human summary).
2. The user asked to **implement** an already-approved Human summary / spec / ADR.
3. The request is a **large product hypothesis** (new segment/Job, value proposition, positioning, "should we build this", live-product diagnosis) — read `.cursor/skills/product-hypothesis/SKILL.md` and use NMT instead.
4. The request is a straightforward **bugfix** with clear repro and no open product decisions.

If excluded, say which gate fired and continue under the normal factory / NMT / clarify-before-action rules.

## Relation to clarify-before-action

- Default uncertainty → `clarify-before-action` (one or two focused questions).
- Explicit grill / stress-test / "resolve the design tree" → this skill (multi-round design tree).
- Do not auto-escalate clarify into grilling.

## Procedure

Interview the user until you reach a shared understanding. Map this as a **design tree**: every decision branches into the decisions that hang off it.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled: the questions you can ask _now_ without guessing at answers you haven't heard yet. Ask the whole frontier in one round: number each question and give your recommended answer. Then wait for the user's answers before the next round.

Each question should be formatted like so:

```
**Q1** — **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

Recommended: <your recommended answer>
```

Each round the user answers reshapes the tree: settled decisions push the frontier outward and unblock questions that depended on them. Recompute the frontier and ask the next round. A question whose answer depends on another question still open in this round belongs to a _later_ round, not this one.

Finding _facts_ is your job, never the user's. When a frontier question needs a fact from the environment (filesystem, tools, etc.), look it up (or dispatch a sub-agent); don't ask the user for anything you could look up yourself. Don't block on it: a running exploration is an unsettled prerequisite, so only the questions downstream of it wait; ask the rest of the frontier now. The _decisions_ are the user's: put each to them and wait.

Prefer grounding recommendations in this repo's sources of truth: `apps/zarya-tg/docs/prd.md`, `apps/zarya-tg/docs/decisions/`, `apps/zarya-tg/docs/specs/`, `process/ai-factory/`.

The session is done when the frontier is empty: every branch of the design tree visited, nothing left silently assumed. Do not act on the outcome (write specs, tickets, or code) until the user confirms you have reached a shared understanding.
