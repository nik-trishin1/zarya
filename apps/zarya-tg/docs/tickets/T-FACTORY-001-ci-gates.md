# T-FACTORY-001 — CI gates + Railway log scan

## Human summary (review this first)

**Will do:**
- Add GitHub Actions so every PR runs backend tests and frontend lint/build
- Add a CI job that, when Railway credentials are configured, pulls recent Railway deploy (and HTTP 5xx) logs and fails if error signatures appear
- Fix existing frontend lint errors so the new lint gate is green

**Will not do:**
- Change product features or deploy to Railway from this ticket
- Require Railway secrets on forks (scan skips cleanly when token is missing)

**Touched areas (plain language):**
- CI config, frontend lint hygiene, portable Railway log script

**Risk:** Low — CI-only; skip path for missing secrets avoids false failures on forks

**Smoke check after merge:**
- Open a PR → backend + frontend jobs green; Railway job either skips or scans without error

**Reviewer decision:** `[x] Approved to implement` · Reviewer: factory-pilot · Date: 2026-07-24

---

## Metadata

| Field | Value |
|-------|-------|
| ID | T-FACTORY-001 |
| Title | CI gates + Railway log scan |
| Status | `done` |
| Spec / ADR | [process/ai-factory/CI.md](../../../../process/ai-factory/CI.md) |
| Estimate | S |

## Goal

Make automated verification the merge gate, including optional production log inspection on Railway.

## Acceptance criteria

- [x] `.github/workflows/ci.yml` runs pytest (backend) and lint+build (frontend) on PRs to `main`
- [x] Railway log scan job uses `process/ai-factory/scripts/check-railway-logs.sh` and skips when `RAILWAY_TOKEN` is unset
- [x] Frontend `npm run lint` and `npm run build` pass locally
- [x] Backend `PYTHONPATH=. pytest -q` passes locally
- [x] PR template references CI + Railway scan

## Out of scope

- Configuring GitHub secrets/vars in the Railway/GitHub UI (operator step; documented)
- E2E Telegram testing

## Verification

1. [x] Backend pytest
2. [x] Frontend lint + build
3. [ ] CI green on PR (after push)
4. [x] Review pass requested via factory pilot notes
