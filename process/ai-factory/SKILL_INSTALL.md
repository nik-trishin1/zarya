# Third-party skill install SOP (portable)

Gate for any skill, plugin, or rules pack that did not originate in this repo. A skill is executable instructions with repo and shell access: treat it like a dependency.

## Default stack

AI-Factory (`process/ai-factory/`) + Next Move Theory (`.cursor/skills/product-hypothesis/`, `nmt-*`) + the adapted productivity skills (`.cursor/skills/matt-pocock-productivity/README.md`).

**Not default, not installed:** Superpowers, GSD, marketing "exoskeleton" packs, and other all-in-one workflow bundles. They duplicate Factory gates (DoR, review pass) and add always-loaded context. Reconsider only after a pilot (step 4) shows a gap the default stack cannot close.

## Steps (one skill at a time)

1. **Need.** Name the concrete gap in one sentence and the Factory/NMT step that fails today. No named gap, no install.
2. **Audit (human-owned).** The human reads every file in the skill and confirms each item:
   - [ ] Source is a known author or repo; version/commit pinned.
   - [ ] No network calls, `curl | bash`, or downloads of other code.
   - [ ] No reads of secrets, `.env`, tokens, or `~/` outside the repo.
   - [ ] No writes outside the paths the skill documents; no edits to `AGENTS.md`, rules, or CI.
   - [ ] No instructions to disable review gates, bypass approvals, or hide actions.
   - [ ] Always-loaded text (description, rules) is short; the body loads on demand.
   - [ ] License allows use.
   An LLM audit prompt or scanner may help find issues; its verdict is advisory. The human owns the security decision.
3. **Install** into a branch, not `main`. Vendored copy with attribution (like `matt-pocock-productivity/`), not a live fetch.
4. **A/B on one real task.** Same ticket with and without the skill. Compare: tokens, review-pass result, rework, conflicts with existing skills.
5. **Decide and record.** Keep, adapt, or remove. Add a short note (why, result, owner) next to the skill; keep it out of always-applied rules.

## Rules

- One skill per PR; no bundles.
- Prefer subtraction: remove an overlapping skill when adding one.
- Never add to always-apply rules to make a skill fire; use a precise description instead (`.cursor/skills/writing-for-agents/SKILL.md`).
- Skills never touch Railway secrets or variables, bot tokens, or production schema.
