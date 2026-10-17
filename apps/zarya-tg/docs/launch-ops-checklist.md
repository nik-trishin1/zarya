# zarya-tg — Launch / ops checklist

Process only: verify and document. No feature work from this list. Status as of 2026-10-17; update the **Status** and **Evidence** columns when an item is checked.

**Status:** `known` = evidence in repo/CI/ticket history · `unknown` = needs a human or dashboard check · `gap` = known not done.

**Do not change without the owner (Nikita):** Railway secrets and variables, bot token, production DB schema.

| # | Item | Status | Evidence / next check |
|---|------|--------|-----------------------|
| 1 | CI Railway log scan has `RAILWAY_TOKEN` (secret) + `RAILWAY_SERVICE_NAMES` (variable) | **gap** | Last `main` CI run (2026-10-16, run 38908051926): job `Railway runtime logs` passed with `Railway log scan skipped: RAILWAY_TOKEN secret not configured.` Vars per [`process/ai-factory/CI.md`](../../../process/ai-factory/CI.md): `RAILWAY_TOKEN`, `RAILWAY_SERVICE_NAMES` (e.g. `zarya-backend,zarya-frontend`), optional `RAILWAY_ENVIRONMENT`, `RAILWAY_PROJECT_ID`, `RAILWAY_LOG_LINES`. Owner action: Settings → Secrets and variables → Actions. |
| 2 | Telegram bot webhook configured | **n/a (polling)** | The bot uses long polling (`dp.start_polling` in `backend/app/bot/handlers.py`; guide checks the `Telegram bot polling started` log line in [`deploy-railway.md`](deploy-railway.md)). No webhook is configured by design. Check instead: exactly one backend process per `BOT_TOKEN` (no local `dev-local.sh` with the prod token). Switching to webhook needs an ADR. |
| 3 | Backend deployed and healthy on Railway | **known (prod running)** | T-213/214/215 confirmed on prod by the owner (see [`tasks-archive.md`](tasks-archive.md)). Recheck: backend logs show `Telegram bot polling started`; `GET <frontend>/api/events` returns `{"detail":"Missing Telegram init data"}`. |
| 4 | Frontend deployed and healthy (static + nginx proxy) | **known (prod running)** | Same evidence. Recheck `API_UPSTREAM` points at backend; `VITE_API_URL` unset ([`deploy-railway.md`](deploy-railway.md) troubleshooting). |
| 5 | Production env sane (`DEV_MODE=false`, `WEBAPP_URL` public HTTPS, `CORS_ORIGINS`) | **unknown** | Dashboard check by owner; not verifiable from repo. |
| 6 | End-to-end run with real Telegram accounts (list → register → cancel → `.ics` → admin `/admin` create/edit) | **unknown** | No recorded e2e run in docs. One non-admin and one admin account; note result under Evidence. |
| 7 | Pilot: invite ~20 users, validate flows | **unknown** | No pilot record found. Define success before inviting: registration completes, reminders arrive, no 5xx in logs. |
| 8 | Triage bugs from the pilot | **unknown** (blocked by 7) | One backlog line per bug in [`tasks.md`](tasks.md); bugfixes skip NMT/DoR. |
| 9 | Optional: Cursor Automation `factory-implement` | **gap (optional)** | Not created. Prompt and operator checklist: [`process/ai-factory/ORCHESTRATOR.md`](../../../process/ai-factory/ORCHESTRATOR.md). Dry-run on one DoR ticket first; no ticket is DoR-ready today (`tasks.md`). |

## Order

1 → 5 (owner, short) → 6 → 7 → 8. Item 9 waits until a DoR-ready ticket exists.

## Open questions for the owner

- Is the pilot already informally running (items 6–7 may be done but unrecorded)?
- Should the Railway scan stay a skip-on-missing-token no-op, or become a required gate once the token is set?
