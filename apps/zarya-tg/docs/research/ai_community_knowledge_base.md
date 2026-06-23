# AI Community Knowledge Base

> Source: Telegram community "Heroes of Magic: AI · GPT · Codex · Claude · Cursor · Zed etc"
> Period: October 2025 — May 2026
> Curated for use in the zarya repository.

This document captures community-validated best practices for AI-assisted development. Sections most relevant to zarya are marked with ★.

---

## ★ Cursor Rules (.mdc) — Best Practices

Cursor rules come in four types, each with a different activation model.

| Type | Activation | Token cost | When to use |
|------|-----------|-----------|-------------|
| Always Apply | Every request | High | Core context, non-negotiable constraints |
| Apply Intelligently | Agent decides | Low | Task-specific guidance |
| Apply Manually | Called via `@` | Zero unless called | Reference material, templates |
| Apply Specific Files | Triggered by file match | Low | Language or framework rules |

**Recommendation:** Keep "Always Apply" rules under ~5k tokens total. Replace broad always-on rules with "Apply Intelligently" where possible to reduce token spend.

**Relevant repos:**
- https://github.com/VsevolodUstinov/ai-first-workspace-template
- https://github.com/VsevolodUstinov/Personal-Super-Agent-Ru
- https://cursor.directory/rules

---

## ★ Context Management

- Do not exceed 40% of the model's context window in a single session.
- At 40-50% context fill, produce a compact handoff summary and continue in a new session.
- Exclude `node_modules/`, `.env`, `__pycache__/`, `.git/`, `dist/`, `build/` from context at all times.
- Decompose large tasks into parallel subtasks to keep the orchestrator context lean.
- Reference lecture: https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/ace-fca.md

> "If tokens are flying fast — it's a signal the task is poorly decomposed." — Nikolai Berezovskii

---

## ★ Spec-Driven Development

Community-validated workflow for AI-assisted coding:

1. Chat with the model to produce a PRD (10-20 min).
2. Break PRD into a task board (~100-200 items).
3. Execute tasks autonomously with plan review and code review gates.
4. Maintain a `project_state` snapshot of the current state.

**Relevant frameworks:**
- GitHub Spec Kit: https://github.com/github/spec-kit
- Agent OS: https://github.com/buildermethods/agent-os
- BMAD Method: https://github.com/bmad-code-org/BMAD-METHOD
- Autocoder workflow: https://github.com/leonvanzyl/autocoder/tree/master

---

## ★ Railway Deployment

Railway connects to GitHub in one click. Push to main → autodeploy. The hobby tier ($5/month) supports multiple services. This matches the zarya deployment strategy.

---

## Agent Architecture Patterns

**Multi-agent quality improvement.** Running several sub-agents independently on the same task and selecting the best result significantly improves quality and repeatability.

**Parallel sub-agents.** Ask the orchestrator to decompose tasks for parallel execution by sub-agents. This saves the orchestrator's context and speeds up execution.

**Session memory hooks.** Claude Code supports hooks that force-load instructions at session start and on each message. Useful for ensuring agents always read the latest `AGENTS.md`.
- Docs: https://code.claude.ai/docs/en/hooks-guide

**Org-chart for agents.** Maintain an `org-chart.md` that maps agents to roles (Engineering, Strategy, Marketing) with recommended models and interaction patterns. Before assigning a task, check which agent is best suited.

---

## Useful Prompts

**Interview before building** (Thariq Shihipar, Anthropic):
```
read this @SPEC.md and interview me in detail using
the AskUserQuestionTool about literally anything:
technical implementation, UI & UX, concerns,
tradeoffs, etc. but make sure the questions are
not obvious

be very in-depth and continue interviewing until
you have a clear picture of what I want to build
```

**Unstick a blocked model.** Repeating the same prompt twice in sequence can unblock a stuck model. The second copy sees the first through the attention mechanism. Source: https://arxiv.org/html/2512.14982v1 (Google Research, won 47/70 tests).

---

## Useful MCP Servers

| MCP | Link | Purpose |
|-----|------|---------|
| Playwright | `npm: @playwright/mcp` | Browser-based automated testing |
| Figma (FigMCP) | https://figmcp.com/mcp | Full Figma control |
| Context7 | https://context7.com | Fresh docs for n8n and others |
| EXA | https://exa.ai/docs/reference/exa-mcp | Semantic search (free tier: 10 req/month) |
| Telegram | https://github.com/chigwell/telegram-mcp | Telegram access |
| Linear | built-in to Claude Code | Task tracking |

---

## Token Economy

**Cost benchmarks (early 2026):**

| Setup | Monthly cost | Best for |
|-------|-------------|---------|
| Cursor Pro + z.ai | ~$23 | Baseline development |
| Cursor Pro + Claude Pro + z.ai | ~$43 | Intensive development |
| VSCode + Claude Pro + ChatGPT Plus | ~$40 | Maximum model variety |

**Token-saving rules reduce spend by ~3x.** Example: a $12 request dropped to $4 after adding lean rules. Source: https://www.cursor-ide.com/blog/claude-sonnet-4-5-pricing

---

## Key Principles

> "Every mistake, every agent gap — becomes a rule in Cursor or a standard, to guide the agent and eliminate incident generators." — Ilya Krasinsky

> "Don't polish a skill until you've tested it in production. Get LLM feedback earlier." — Ilya

> "The best is the enemy of the good. Only update skills when you see a real need." — Alena

> "XML is the optimal data markup for LLMs. Any structuring of input data improves the process." — mr.Dru

> "Data redundancy is harmful. Saving data for the sake of saving data is inefficient." — Claude (via Nikolay K)

---

## Relevant External Resources

| Resource | Link |
|----------|------|
| AI-first workspace template | https://github.com/VsevolodUstinov/ai-first-workspace-template |
| Personal Super Agent | https://github.com/VsevolodUstinov/Personal-Super-Agent-Ru |
| Cursor rules directory | https://cursor.directory/rules |
| Skills marketplace | https://skillsmp.com/ |
| Agent skills library | https://www.aitmpl.com/skills |
| Context engineering lecture | https://www.youtube.com/watch?v=rmvDxxNubIg |
| Vibe Coding roadmap | https://roadmap.sh/vibe-coding |
| Claude Code roadmap | https://roadmap.sh/claude-code |
| Multiagency standards (RU) | https://lively-chive-e7f.notion.site/264a2ada72fc80de8c65fb16df026c9f |
| Advanced context engineering | https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/ace-fca.md |
