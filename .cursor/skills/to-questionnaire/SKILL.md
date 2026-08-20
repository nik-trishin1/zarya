---
name: to-questionnaire
description: >-
  Turn a decision you cannot answer alone into a Markdown questionnaire for the
  person who can fill it in async or in a meeting. Use before DoR when a
  stakeholder holds missing facts. Do not use mid-flight on factory-queued tickets.
disable-model-invocation: true
---

# To questionnaire (zarya-adapted)

Adapted from [mattpocock/skills](https://github.com/mattpocock/skills) `productivity/to-questionnaire` (MIT).

## Hard exclusions

Do not run this skill mid-flight on a **factory-queued** DoR ticket. For factory work, choose safe defaults per `process/ai-factory/DEFINITION_OF_READY.md` or stop only if the change would violate the approved Human summary / ADR.

Prefer this skill **before** enqueueing: when Human summary or DoR is blocked on knowledge held by someone else.

## Procedure

Turn something the user can't answer alone into a **questionnaire**: a Markdown document they hand to one person to fill in async, or fill out together over a meeting. The recipient holds knowledge the user lacks; the questionnaire pulls it out of them.

**Grill the send, not the subject.** Interview the user only about the _send_, which they can always answer: who it goes to, and what they need back. The questions in the document then target the **gap** between what the recipient knows and what the user needs.

1. **Who is it going to?** Ask, in one exchange, the recipient's role, expertise, and relationship to the user. This fixes the questionnaire's tone and how much context it must carry. Done when you know who the recipient is and what they know that the user doesn't.

2. **What do you need back?** Ask, in one exchange, the specific decisions or facts the user can't resolve alone and needs from this person. Done when you have a concrete list of what the user must walk away able to do or decide.

3. **Write the questionnaire.** Draft questions aimed at the gap from steps 1–2, following the Document structure below. Write it to:

   `apps/zarya-tg/docs/questionnaires/to-questionnaire-<slug>.md`

   Create `apps/zarya-tg/docs/questionnaires/` if missing. Slug from the topic (kebab-case). Report the path. Done when the file exists and every item the user named in step 2 is covered by a question.

## Document structure

Frame the document as a **discovery questionnaire**: the user lacks context, the recipient holds it. Order questions most-important-first, since async means you may only get one pass, and group them under `##` headings by theme once there are more than a handful.

```markdown
# <Title>

**Purpose:** why this questionnaire exists and the decision riding on it.

**From:** <sender>
**To:** <recipient>
**How your answers will be used:** <one or two sentences>

## Context

One paragraph orienting a recipient who wasn't in the user's head. Enough to answer well, not a page. Prefer links to `apps/zarya-tg/docs/prd.md`, specs, or ADRs when they exist.

## How to answer

Deadline and rough effort. Partial answers and "I don't know" are useful: flag anything you're unsure of rather than skipping it.

## <Theme>

### <One idea per question>

_Why this matters: <only when the question could be misread>_

> 

## Anything else?

Anything we didn't ask that we should know?
```
