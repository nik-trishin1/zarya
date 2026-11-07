# skill-inspector (vendored for zarya)

On-demand helper for reviewing third-party AI agent skills before install. Wraps [NVIDIA SkillSpector](https://github.com/NVIDIA/SkillSpector) static scans plus source-aware semantic review.

**Not always-apply.** Load only when auditing a skill (see `process/ai-factory/SKILL_INSTALL.md`).

## Upstream

- Source: https://github.com/NVIDIA/SkillSpector/tree/main/skills/skill-inspector
- Pinned commit: `e48d771a26f7398b36256ceb8d8f94adce3d5c44` (SkillSpector v2.12.0)
- License: Apache-2.0 (see `LICENSE`)

## Pre-install self-scan

```text
skillspector scan .cursor/skills/skill-inspector --no-llm
```

Recorded result (this drop):

| Field | Value |
|-------|--------|
| Score | 0 / 100 |
| Severity | LOW |
| Recommendation | SAFE |
| `llm_requested` | false |
| Scanner | SkillSpector v2.12.0 @ `e48d771a…` |

Score is advisory; humans still complete the `SKILL_INSTALL.md` checklist for any skill under review.
