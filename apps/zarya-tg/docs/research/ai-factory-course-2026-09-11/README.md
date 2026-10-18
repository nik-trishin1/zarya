# AI Factory course notes — 2026-09-11

> **Status:** research / input for planning — **not** an ADR and not Definition of Ready.  
> Use this to compare against `process/ai-factory/` and decide what to adopt for zarya.

| Field | Value |
|-------|-------|
| Meeting | AI agents and software development process — building predictable products |
| Date | 2026-09-11 |
| Speaker | Alexey Kulichevskiy (vibecamp / Продуктостроение) |
| Participant (listener) | Nikita Trishin |
| Sources | Live transcript + slides + Telegram Soft Factory demo |
| Slides | `slide-*.png` in this folder |
| Related repo process | [`process/ai-factory/`](../../../../../process/ai-factory/) |

---

## Key theses (canonical summary)

1. **Process > model.** A stronger model without a visible process still yields a lottery. Predictability comes from controlling every development stage, not from a better subscription.
2. **One-shot for yourself ≠ product work.** Chat-and-ship works for personal toys, landings, scripts, prototypes. The moment you iterate a shared product (or a business), context loss and regressions dominate unless stages are explicit.
3. **LLMs are stateless text→text.** Memory, tools, and “agents” live in the **harness** (system prompt, history, RAG, tools). Never assume the model “remembers” prior product decisions unless those decisions are on disk and re-injected.
4. **Two hard failure modes of endless chat:** (a) **reinventing the wheel / Frankensteining** (new parallel abstractions instead of extending existing ones); (b) **context overflow / contradiction soup** (window fills; mid-session decisions are forgotten).
5. **Make the cycle visible.** Classic stages always exist (task → design → tickets → code → test → publish → accept). Owners often only see start and end; agents (like weak teams) skip the middle unless you force artifacts and gates.
6. **Artifact at every stage; then reset context.** End each stage with a file (or PR / ticket) outside the model. Clear the session. Start the next stage with a fresh model that reads the artifact — not chat history.
7. **Strong team = strong process (with or without AI).** Detailed elaboration, well-described tasks, strict testing, careful deploy. Weak team = code without elaboration, “figure it out later,” test on users → **random** quality.
8. **Factory ≠ always better.** Spectrum from craftsperson (HITL, high craft) to factory (AFK, volume, sameness, predictability). Choose position on the spectrum by stakes and product stage — do not cargo-cult a full factory for a one-off.
9. **Human owns intent; agents own execution after tickets.** Kulichevskiy’s operating point: stay in loop through **elaboration → plan → tickets**; then release agents for code → review → (optionally) merge/deploy. Proof of work via screenshots/video when not reading every line.
10. **Code-writing skill declines in leverage; process skill rises.** Bottleneck should not be a human reading every PR when many agent streams run in parallel — compensate with harsh automated gates (unit / integration / mutation / complexity / security review).
11. **Verification is dual:** deterministic (tests + CI) and probabilistic (another model reviewing against ticket AC + project standards). Code ↔ review loop until both say pass.
12. **Production monitoring closes the loop.** Errors/metrics become tickets; tickets become PRs; green PRs ship — “incident overnight, fixed by morning.”
13. **Factory is modular plumbing, not one magic agent.** Models + harnesses + GitHub + automated tests + auto-deploy + Docker + Sentry/PostHog + Linear (or equivalent) wired so error → ticket → PR → server.
14. **Telegram Soft Factory demo pattern:** natural-language ask → manager agent elaborates export shape / isolation / tests → human confirms with «делай» (or corrects) → ticket → implementer → reviewer → PR → deploy ask. Human is acceptance owner, not coder.

---

## Development stages (always present)

From the slide *«Процесс разработки»* — business owner sees **start and end**; middle is invisible unless made explicit:

| # | Stage (RU) | Stage (EN) | Owner-visible? |
|---|------------|------------|----------------|
| 1 | Поставить задачу | Set the task | Yes |
| 2 | Спроектировать решение | Design the solution | Usually hidden |
| 3 | Разбить на задачи | Break into tasks | Usually hidden |
| 4 | Написать код | Write code | Usually hidden |
| 5 | Протестировать | Test | Usually hidden |
| 6 | Опубликовать | Publish / deploy | Usually hidden |
| 7 | Принять результат | Accept the result | Yes |
| (8) | Поддержка / мониторинг | Support / monitoring | Often forgotten |

> «Владелец бизнеса видит начало и конец. Середину видят только разработчики.»

---

## Visible AI cycle (six cards)

From the slide *«Решение: сделать цикл видимым»*:

| Stage | What happens | Artifact / tool |
|-------|--------------|-----------------|
| **1. Проработка (Elaboration)** | Model asks questions until shared understanding | `spec.md` (or `intent.md`) |
| **2. План (Plan)** | Fresh model reads spec + code; lists files to touch and outcomes | `plan.md`, commit |
| **3. Тикеты (Tickets)** | Plan → work units; dependent sequential, independent parallel | Linear / Jira / ticket files |
| **4. Код (Code)** | Fresh model gets goal + context + **one** ticket; does only that | Pull request |
| **5. Проверка (Verification)** | Tests + review vs acceptance criteria; nothing old broken | CI + review |
| **6. Слияние (Merge)** | Only what passed verification enters the product | `main` |

**Core operating rule (slide):**

> At the end of each stage the result goes to disk, context is cleared, and the next stage is done by a **fresh model** — not from chat memory, but **from the file**.

---

## Stage deep-dive (from talk)

### 1. Elaboration (`spec.md`)

- **Input:** raw idea (text, voice, Telegram).
- **Goal:** shared understanding — what problem, what behavior, what order, what is out of scope.
- **Technique:** model grills the human (e.g. Matt Pocock–style `grill-me` / relentless Q&A) until ambiguity is gone.
- **Output:** markdown spec on disk.
- **Then:** kill the session.

### 2. Plan (`plan.md`)

- **Input:** approved spec only (fresh context).
- **Work:** explore current code and options.
- **Output:** which files change, what changes, desired result, **evaluation criteria** — still not the final implementation detail dump as “done work.”
- **Then:** kill the session.

### 3. Tickets

- **Input:** plan (+ spec).
- **Output:** board cards or `task-1.md`… files, each with:
  - what to do
  - acceptance criteria
  - how to test / how to know done
- Dependent tickets serial; independent tickets parallel.

### 4. Code → PR

- Give model: **big goal + plan + this one ticket** (full intentional context, small scope).
- Agent works on an isolated branch.
- Output is a **pull request**, not a silent merge — because agents err like humans.

### 5. Verification (loop with coding)

Two layers:

| Kind | Mechanism | Role |
|------|-----------|------|
| Deterministic | Automated tests (positive + negative cases); full suite on every PR | Catch regressions when agent rewrites unrelated code |
| Probabilistic | Second model code review | Matches ticket AC? Project standards? Security? Cleanliness? Performance? |

CI + review must both pass. Reviewer sends coder back until green.

### 6. Deploy

- Ship to the environment clients use.
- Automate carefully so deploy is uneventful.
- Higher-stakes orgs keep a **human gate** before production merge/deploy.

### 7. Support / monitoring (mentioned, left partially out of scope)

- Production errors → auto ticket → diagnose → fix PR → review → deploy.
- Human sees morning summary: incident happened, pipeline fixed it.

---

## AFK ↔ HITL spectrum

| Pole | Meaning |
|------|---------|
| **HITL** (Human in the Loop) | Human participates at stages |
| **AFK** (Away From Keyboard) | Autonomy when human is absent |

Absurd extremes: no AI at all ↔ AI sets its own goals and ships alone. Real teams sit in between.

**Speaker’s operating point (slightly right of center):**

- Human: task setting, elaboration, plan quality, ticket quality.
- Agents: implement tickets, review, push toward deploy.
- Proof: screenshots / video of UI, not full manual code read of every stream.
- Trust for merge/deploy only because **gates are harsh**.
- Serious B2B (e.g. multi-million clients): keep final accept human.

**Craftsperson vs factory metaphor:**

- Craftsperson: unique, high-touch, expensive, artisanal quality.
- Factory: many identical predictable units on schedule.
- Neither is universally “better”; pick by need (one-off toy vs ongoing product).

---

## Soft Factory live demo (CRM CSV export)

Natural-language request (voice → Telegram): add «скачать как CSV» for all deals.

Observed agent behavior:

1. Manager agent reads skills (`to-tickets`), searches codebase (`export|csv|…`), reads `DealsPage.tsx` / types.
2. Proposes: button on Deals; all deals regardless of filters; columns listed; Cyrillic/quoting/Excel injection care; **tenant isolation**.
3. Asks human to confirm export composition and acceptance ownership → «делай».
4. Creates Linear ticket → implementer on isolated branch → completeness / isolation / download tests → reviewer permission → review → PR path toward deploy.

**Lesson for zarya:** intake can be chatty; **commitment** happens only after a written proposal the human accepts.

---

## What the factory consists of (slide)

| Block | Examples / role |
|-------|-----------------|
| Models | Fable, Codex, DeepSeek — pick consciously; one may not be enough |
| Harnesses | Claude Code, Codex, Cursor, Hermes — how the model reads files and runs commands |
| GitHub | Version control: truth in the repo, not in chat |
| Automated testing | Checks new code before humans see it |
| Automated publish | Green checks → server |
| Docker | Isolate runtime so agents cannot brick the host casually |
| Sentry + PostHog | Errors and behavior visible; error can become a ticket |
| Linear (or equiv.) | Work queue: monitoring enqueues, agents dequeue |

> Any single tool can be learned quickly. Hard part: wire them so **error → ticket → PR → server**.

---

## When to use a factory (decision heuristic)

| Situation | Prefer |
|-----------|--------|
| One-off for yourself; landing; script; throwaway prototype; “feel the magic” | Direct chat with a model (craft / HITL light) |
| Ongoing product; multiple contributors/agents; need predictability, measurability, safe iteration | Visible process + selective automation (factory) |
| High financial / safety stakes | Factory **plus** human final accept |

---

## Mapping to current zarya AI-Factory

Existing portable playbook: [`process/ai-factory/`](../../../../../process/ai-factory/).

| Course stage | Already in zarya? | Notes / planning gaps |
|--------------|-------------------|------------------------|
| Elaboration → `spec.md` | Partial | Specs + Human summary + NMT for large bets; grilling skill exists. Intake from Telegram Soft Factory not wired. |
| Plan → `plan.md` | Weak / ad hoc | No mandatory `plan.md` artifact or fresh-session plan gate before tickets. |
| Tickets | Strong | `docs/tickets/`, DoR, Human summary, Linear optional via orchestrator docs. |
| Code → PR | Strong | Cloud Agent / Cursor Automation prompt in `ORCHESTRATOR.md`. |
| Verification | Partial | CI (pytest, lint/build, Railway log scan). Separate `REVIEW_PASS.md`. Mutation / complexity gates not as aggressive as speaker’s stack. |
| Merge / deploy | Partial | Human merge expected; Railway deploy; auto-merge not default. |
| Monitoring → ticket | Gap | No Sentry/PostHog → auto-ticket loop called out in course. |
| Multi-agent manager/coder/reviewer | Partial | Review gate exists; “manager proposes then waits for «делай»” Soft Factory not built. |
| Proof of work (video/screenshots) | Emerging | Walkthrough artifacts skill exists; not yet a hard factory AC. |

**Planning use:** treat this folder as input when deciding the next process ADR / factory upgrade (e.g. mandatory plan artifact, monitoring loop, Telegram intake, stricter CI). Do **not** silently expand product MVP scope from this research.

---

## Course logistics (context only)

- Course starts ~21 September (as stated in talk).
- Small groups (max ~10), paid offering — **not** a zarya product requirement.
- Capstone idea on the course: build a small-business CRM end-to-end as a sandbox for factory skills (landing, auth, DB models, UI, API, email, payments, analytics). Transferable patterns for any full product — including zarya’s stack shape (frontend / backend / DB / monitoring).

---

## Slide index (saved assets)

| File | Content |
|------|---------|
| `demo-telegram-factory.png` | Soft Factory Telegram demo (CSV export proposal) |
| `slide-dev-process-owner-sees-ends.png` | Owner sees task + accept; middle faded |
| `slide-strong-vs-weak-team.png` | Good team = good process |
| `slide-visible-cycle.png` | Six-stage visible cycle + fresh-model rule |
| `slide-factory-components.png` | Models, harnesses, GitHub, tests, deploy, Docker, Sentry/PostHog, Linear |

---

## Suggested next planning questions (for a later session)

1. Do we add a mandatory **plan artifact** gate between approved spec and ticket split?
2. Where should zarya sit on **AFK↔HITL** for merge — keep human merge, or allow auto-merge after green CI + review PASS?
3. Is **production error → ticket** (Sentry) worth an ADR in Iteration 2+?
4. Do we want a **Telegram / chat intake** that only creates tickets after human «делай» on a written proposal?
5. Which CI gates from the “harsh verification” list are worth adopting next (beyond current pytest/lint/Railway scan)?
