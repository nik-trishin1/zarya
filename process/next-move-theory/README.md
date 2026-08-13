# Next Move Theory (portable)

This folder documents how zarya vendors Ivan Zamesin's **Next Move Theory** canon and skills for **large product hypotheses** — deciding *what* to build and *for whom* before AI-Factory tickets exist.

Canon and skills are **not** authored here. They come from the public repo:

[github.com/zamesin/Next-Move-Theory-Canon-and-Skills](https://github.com/zamesin/Next-Move-Theory-Canon-and-Skills)

License: [CC BY-NC-SA 4.0](LICENSE) (see [NOTICE.md](NOTICE.md)). Applying the methodology to a product is allowed; do not resell or re-publish the material as a paid course.

Installed methodology version: repo-root `.nmt-version`.

## What lands in a consuming repo

The official installer writes these paths (keep the canon folder name exact — skills resolve it relatively):

| Path | Role |
|------|------|
| `Next-Move-Theory-Canon/` | Methodology theses (AJTBD, RAT, ABCDX, the algorithm) |
| `.claude/skills/nmt-*` | Claude Code skills (`/nmt-…`) |
| `.agents/skills/nmt-*` | Codex skills (`$nmt-…`) |
| `.cursor/skills/nmt-*` | Same Codex-flavored skills, copied for Cursor discovery |
| `.cursor/skills/product-hypothesis/` | Cursor front door / router (this repo) |
| `AGENTS.md` / `CLAUDE.md` | Rules block between `<!-- Next-Move-Theory-Rules:… -->` markers |
| `NextMoveTheory-README.md` | Upstream README, renamed so it does not clobber the project README |

Cursor-specific extras in this repo:

- `.cursor/rules/next-move-theory.mdc` — apply-intelligently rule (large bets only)
- `apps/zarya-tg/docs/research/nmt/` — default place to save hypothesis artifacts
- `Skills-Results/` — gitignored; unused unless someone asks for the upstream default

## When to use it

Use NMT when the question is strategic: segment + Job, value, positioning, PMF, "should we build this", live-product diagnosis, interview synthesis.

Do **not** use it for factory-queued tickets, bugfixes, or implementing an already-approved spec. Those stay on [`ai-factory/`](../ai-factory/).

## Cursor vs Claude Code vs Codex

Producer skills mention Claude `AskUserQuestion` or Codex `request_user_input`. In **Cursor**, ask the same questions in chat and wait. Deep mode: use Cursor `Task` subagents + `WebSearch` / `WebFetch`.

Default output path in this repo is `apps/zarya-tg/docs/research/nmt/`, not `Skills-Results/`.

## Relation to AI-Factory

```
large hypothesis → NMT skill (hypotheses + RAT)
  → cheapest field test
  → human accepts direction
  → spec (Human summary) + ADR if scope changes
  → DoR tickets → factory implement
```

An NMT "PRD" is still a **value hypothesis**. It is not Definition of Ready.

## Install / update

From the **repo root**:

```bash
curl -fsSL https://nextmovetheory.com/install.sh | bash
bash process/next-move-theory/sync-cursor-skills.sh
```

The first command refreshes the canon, `.claude/skills`, `.agents/skills`, `NextMoveTheory-README.md`, `.nmt-version`, and the marked rules blocks (project text outside the markers is kept). The second copies Codex skills into `.cursor/skills/` and **does not** delete `product-hypothesis`.

Alternatively invoke the vendored `nmt-upgrade` skill, then run the sync script.

## Skills (invoke by asking, or by reading the SKILL.md)

| Skill | Use |
|-------|-----|
| `product-hypothesis` | Cursor router — start here if unsure |
| `nmt-chat` | Conversational advisor; paste messy context |
| `nmt-diagnose` | Live product: risks, growth points, next move |
| `nmt-market-research` | New idea: segment + Jobs, GO / NARROW / PIVOT |
| `nmt-analyze-interviews` | Extract AJTBD structure from interview files |
| `nmt-craft-value-proposition` | Value hypotheses + RAT cards |
| `nmt-product-requirements` | Build-oriented spec (still a hypothesis) |
| `nmt-craft-go-to-market` | Landing / ads / growth communication |
| `nmt-upgrade` | Re-run the official installer |

`nmt-chat` and `nmt-diagnose` are the two front doors. The four producers form a pipeline: market-research → value proposition → product-requirements and/or go-to-market.
