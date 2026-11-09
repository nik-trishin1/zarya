# Vendored skill

Upstream: https://github.com/MainFrame100/quality-check-skill  
Author: Dmitrii Yuzhanin  
License: CC BY 4.0 (see LICENSE, ATTRIBUTION.md)  
Upstream version: 1.1.0 (2026-06-25)

Copied from the **ELAVIS** adaptation of upstream
(`nik-trishin1/elavis` → `.cursor/skills/quality-check/`), then lightly
re-layered for Zarya. Protocol sections 1–11 are unchanged from upstream;
only the project layer (SoT, placement, follow-up gates) differs.

Zarya uses this as the **structured evidence-quality protocol** for long AI
artifacts (research, briefs, reports, strategies, ticket/spec reviews).

After this protocol, request a separate review pass via
`process/ai-factory/REVIEW_PASS.md`. Lightweight always-on checks:
`.cursor/rules/self-check.mdc`. There is no `outbound-copy-review` in this
repo; Russian UI/bot copy stays Russian.

Update from upstream (or re-sync from elavis):

```bash
# Prefer re-copy from elavis adaptation, then re-apply Zarya layer:
#   .cursor/skills/quality-check/ in nik-trishin1/elavis
# Or from upstream:
git clone --depth 1 https://github.com/MainFrame100/quality-check-skill /tmp/quality-check-skill
cp /tmp/quality-check-skill/quality-check/SKILL.md /tmp/qc-upstream-SKILL.md
cp /tmp/quality-check-skill/LOGIC.md .cursor/skills/quality-check/references/logic.md
cp /tmp/quality-check-skill/VALIDATION.md .cursor/skills/quality-check/references/validation.md
cp /tmp/quality-check-skill/ATTRIBUTION.md .cursor/skills/quality-check/ATTRIBUTION.md
cp /tmp/quality-check-skill/LICENSE .cursor/skills/quality-check/LICENSE
# Then re-apply Zarya layer in SKILL.md (SoT, placement, REVIEW_PASS) — do not overwrite blindly.
```

When adapting, keep `metadata.author`, `metadata.source`, license attribution,
and indicate changes (`metadata.adapted_for`, version suffix).
