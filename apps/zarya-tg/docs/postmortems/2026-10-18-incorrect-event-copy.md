# Postmortem: wrong guest copy and a missing event description in production

**Date:** 2026-10-18
**Status:** Corrected on `main` (`8576602`). Guards from this note are the follow-up.
**Impact:** Event details showed `Гостей: 0 из 15 + Плюша`. Descriptions that never got stored rendered as a missing field. The new-event announcement placed the description after the link.

## What shipped

Three separate drifts, all user-visible, none of them a database outage.

| Drift | Where it lived | What production did |
| --- | --- | --- |
| Guest count suffix `+ Плюша` | `frontend/src/utils/format.ts` | Every details screen appended a name ADR-012 does not contain |
| Empty description accepted | Bot create/edit FSM since the MVP | A message with no text (sticker, photo without using the caption) stored `""` and moved on |
| Description after the link | `build_new_event_announcement` | ADR-011 draws the description above the link. The code appended it inside the share block, under the URL |

The Mini App hides an empty description. A failed bot step therefore looks like a layout bug: the field is simply absent.

## Timeline

| When | What |
| --- | --- |
| 2026-06-23 | ADR-012 locks the guest line to `Гостей: X из Y` / `Гостей: N`. The bot stores `message.text or ""` and always advances. |
| 2026-06-24 | `d6b8658` makes share text `title / link / description` and reuses that helper for the announcement. ADR-011 still shows the description **before** the link. Tests assert the new helper order, so they lock the drift. |
| 2026-06-24 | `c4dd545` (Cursor Agent, one file) appends `+ Плюша` to both frontend return strings. Parent is `d6b8658`. No test. ADR-012 is not updated. |
| 2026-07-16 | `handoff.md` records the suffix as current product behavior. Later sessions treat the handoff as the spec. |
| 2026-07-24 | CI arrives: pytest, frontend lint, frontend build, optional Railway log scan. None of these compare a Russian string to an ADR. |
| 2026-08-18 | ADR-011 price addendum keeps “description, then link”. Code and tests stay on “link, then description”. CI stays green. |
| 2026-10-18 | Production screenshot. Fix `8576602` lands on `main` by fast-forward. |

`Co-authored-by` on those agent commits is the Cursor trailer for the repo owner. It is not a record of a second person reviewing the diff.

## Why CI stayed green

Each check answered a question that was not “does this string match the ADR?”

- **Backend pytest** covered `format_guest_count`, which stayed correct. The frontend formatter was a second copy with no test, so the two diverged forever.
- **Announcement tests** required `message.endswith(share text with the description after the link)`. A change that followed ADR-011 would have failed CI. The tests protected the bug.
- **Frontend CI** is `eslint` and `tsc` plus Vite. Both pass with any Russian string.
- **Railway log scan** looks for tracebacks and HTTP 5xx. Wrong copy does not throw.
- **Review prompt** (`process/ai-factory/REVIEW_PASS.md`) asked for acceptance criteria, scope, and “strings are in Russian”. `+ Плюша` is Russian. It did not ask whether the string is the one in the ADR.
- **`main` accepted a direct push** on 2026-10-18 (`992a856..8576602`). Status checks did not block that update. CI on `main` runs after the commit is already the deploy branch.

The suffix also survived every later pull request because no diff touched that line. CI only re-reads files the new PR changes when a human looks. An untouched wrong line is invisible.

## Cause

The production strings were whatever the last agent commit wrote, as long as the process was syntactically valid.

Three amplifiers made that durable:

1. **Two sources of truth.** ADR-012 / ADR-011 said one thing. The handoff and the tests said another. Agents followed the nearer document.
2. **A correct UI hid a bad write.** Empty description is not rendered, so the bug was reported as a missing field rather than “the bot stored nothing”.
3. **No string contract in the required CI job.** Lint, types, and exception logs cannot see this class of bug.

## What this is not

- Not a failed migration. `events.description` is still the column the API returns.
- Not proof of what one admin typed for Halloween Party. The screenshot has no description block, and the client renders that block only for non-empty text, so the stored value was empty. The caption/empty-message path is the code path that creates that state. It is the mechanism, not a reconstruction of that session.
- Not a reason to treat every `Co-authored-by` trailer as approval.

## Corrections already on main

`8576602` (`fix(zarya-tg): show event description and drop guest-count suffix`):

- Guest line matches ADR-012.
- Create/edit keep `plain_user_text` (text or caption) and stay on the step when it is empty.
- Announcement puts the description before the link and caps it so the link remains.
- Admin cards label `Описание:`.

An event already saved with an empty description stays empty until someone enters the text again in «Редактировать».

## Guards

| Guard | What it catches |
| --- | --- |
| `backend/tests/test_copy_contract.py` | Frontend guest templates drift from `format_guest_count` / ADR-012; `Плюша` returns anywhere under `frontend/src`; create/edit description drops a caption or advances on empty |
| Announcement tests | Description after the link, or a long description eating the link |
| `.cursor/rules/copy-contract.mdc` | Next agent treats a handoff or a green lint as permission to change copy |
| Review check in `process/ai-factory/REVIEW_PASS.md` | Reviewer signs off on Russian text that is not the spec text |

## Residual risk

- CI still has no screenshot of the details screen. A layout break that keeps the same strings will pass.
- Direct push to `main` is still possible with the credential used on 2026-10-18. Turning on branch protection that requires the backend job is a human GitHub setting; this note cannot flip it.
- Admins must re-enter descriptions that were stored as empty.
