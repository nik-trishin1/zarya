# T-208 — Access groups (Core + scalable membership)


## Human summary (review this first)

**Will do:**
- Add named access groups with many-to-many membership (seed Core; silent Core membership for `user_id=1` if present)
- Let admin pick event audience: all bot users or one group
- Hide group events from non-members (admins still see all); block +1 and share on group events
- Scope new-event announce and a new «Написать группе» broadcast to group members only
- Welcome DM when someone is added via the membership service (`notify=True`)

**Will not do:**
- Access-code redemption UI (deferred; same membership table later)
- Admin UI to manage memberships / full Core roster (ops follow-up after you send the list)
- Multi-group audience on one event; changing audience on edit

**Touched areas:** DB schema, event list/detail/register API, admin create + broadcast bot flows, Mini App event details (+1 / share flags)

**Risk:** Medium — wrong recipient list on announce would spam all users; announce must use group members only when audience is a group

**Smoke check after merge:**
- Automated: pytest visibility/+1/announce recipient matrix; frontend lint/build
- Manual post-release (operator): create Core event with notify → only Core (at least `user_id=1`) gets DM; no all-user blast. Public event still has +1 and share.
- Agent CI must **not** send production «notify all» Telegram messages

**Reviewer decision:** `[x] Approved to implement` · Reviewer: product (chat) · Date: 2026-07-24

---

| Field | Value |
|-------|-------|
| ID | T-208 |
| Title | Access groups for closed events |
| Status | `in_review` |
| Spec / ADR | [ADR-020](../decisions/020-access-groups.md) |
| App | `zarya-tg` |
| Estimate | L |

## Goal

Support closed group events and group-scoped messaging without breaking public MVP flows; keep the door open for access codes later.

## Acceptance Criteria

- [x] Tables `access_groups` + `group_memberships`; `events.audience_group_id`; seed Core; silent Core membership for `user_id=1` when that user exists
- [x] `GET /api/events` and detail hide group events from non-members (404); admins see them
- [x] Group events reject `party_size > 1` and PATCH +1; responses expose `allows_plus_one` / `allows_sharing` false
- [x] Mini App hides +1 and «Поделиться» when flags are false; public events unchanged
- [x] Admin create flow chooses audience; notify fans out only to that audience (group members or all users)
- [x] Admin «📢 Написать группе» sends only to group members
- [x] `add_user_to_group(..., notify=True)` sends the Russian welcome DM on first join
- [x] Backend tests cover visibility, +1 gate, announce recipient scoping; frontend lint/build pass

## Out of Scope

- Access codes UI / generation (T-201 remains blocked)
- Membership management in bot or Mini App
- Editing event audience after create
- Seeding the full Core roster (follow-up after operator list)

## Implementation Notes

- Key files: models, `schema_updates.py`, `services/access_groups.py`, `services/events.py`, bot handlers/keyboards/states, `EventDetails.tsx`, `client.ts`
- Deprecate `events.tier` for ACL — use only `audience_group_id`
- Schema seed must not send Telegram welcome to `user_id=1`

## Verification

1. [x] `PYTHONPATH=. pytest -q` in backend (75 passed)
2. [x] `npm run lint && npm run build` in frontend
3. [ ] CI green
4. [ ] Review pass against AC
5. [ ] Operator post-release: Core event + notify → only Core members

## Handoff (when done)

- PR URL: https://github.com/nik-trishin1/zarya/pull/11
- Defaults: admin bypass via `ADMIN_TELEGRAM_IDS`; Core seed + optional `user_id=1` membership; access codes deferred
- Residual risks: concurrent capacity races unchanged; wrong audience selection in create FSM if admin mis-taps
