# zarya-tg — Launch / ops checklist

Process only: verify and document. No feature work from this list. Status as of 2026-11-26 (items 1, 3, 5 rechecked); update the **Status** and **Evidence** columns when an item is checked.

**Status:** `known` = evidence in repo/CI/ticket history · `unknown` = needs a human or dashboard check · `gap` = known not done.

**Do not change without the owner (Nikita):** Railway secrets and variables, bot token, production DB schema.

| # | Item | Status | Evidence / next check |
|---|------|--------|-----------------------|
| 1 | CI Railway log scan has `RAILWAY_TOKEN` (secret) + `RAILWAY_SERVICE_NAMES` (variable) | **gap** | Re-verified 2026-11-26. Workflow wiring is correct: job `railway-logs` in [`ci.yml`](../../../.github/workflows/ci.yml) passes `secrets.RAILWAY_TOKEN` and `vars.RAILWAY_SERVICE_NAMES` / `RAILWAY_ENVIRONMENT` / `RAILWAY_PROJECT_ID` / `RAILWAY_LOG_LINES` to `process/ai-factory/scripts/check-railway-logs.sh`. Latest `main` CI run (2026-11-18, run 44251904427) still prints `Railway log scan skipped: RAILWAY_TOKEN secret not configured.` (`RAILWAY_SERVICE_NAMES` was empty too). Secret/variable values and existence are not readable by agents (GitHub API 403) — **owner must set by hand**: Settings → Secrets and variables → Actions → secret `RAILWAY_TOKEN` (Railway project token, `zarya-friends` / production) and variable `RAILWAY_SERVICE_NAMES` = `be,fe` (real Railway service names; the `zarya-backend,zarya-frontend` example in `CI.md` does not match prod). Optional: `RAILWAY_ENVIRONMENT=production`. After setting, re-run CI on `main` and expect `Deploy logs: service=be …` instead of `skipped`. Once the token is set the job fails on `Traceback`, `CRITICAL`, `Unhandled`, ` ERROR `, `Exception:`, `FATAL`; prod logs currently contain transient aiogram polling retries (Telegram `Bad Gateway` / timeouts) that look like `ERROR:aiogram.dispatcher:…` — watch the first runs for false positives and tune `RAILWAY_ERROR_GREP` only with the owner. |
| 2 | Telegram bot webhook configured | **n/a (polling)** | The bot uses long polling (`dp.start_polling` in `backend/app/bot/handlers.py`; guide checks the `Telegram bot polling started` log line in [`deploy-railway.md`](deploy-railway.md)). No webhook is configured by design. Check instead: exactly one backend process per `BOT_TOKEN` (no local `dev-local.sh` with the prod token). Switching to webhook needs an ADR. |
| 3 | Backend deployed and healthy on Railway | **known (prod running; rechecked 2026-11-26)** | T-213/214/215 confirmed on prod by the owner (see [`tasks-archive.md`](tasks-archive.md)). Recheck: backend logs show `Telegram bot polling started`; `GET <frontend>/api/events` returns `{"detail":"Missing Telegram init data"}`. | Rechecked 2026-11-26: `be` and `fe` deployments `SUCCESS` (last deploy 2026-11-18), `Postgres` `SUCCESS`; `GET /api/events` → `401 Missing Telegram init data`; 7-day 5xx rate 0% on both (only ~5 requests — no real traffic yet); latest `be` runtime logs (101 lines) contain only transient aiogram `Bad Gateway` / timeout retries followed by `Connection established`, no tracebacks. The `Telegram bot polling started` line is outside the log window — it appears only at process start.
| 4 | Frontend deployed and healthy (static + nginx proxy) | **known (prod running)** | Same evidence. Recheck `API_UPSTREAM` points at backend; `VITE_API_URL` unset ([`deploy-railway.md`](deploy-railway.md) troubleshooting). |
| 5 | Production env sane (`DEV_MODE=false`, `WEBAPP_URL` public HTTPS, `CORS_ORIGINS`) | **known (mostly) — owner confirms values** | Read-only check 2026-11-26 (Railway project `zarya-friends`, env `production`, service `be`; no variables changed, no values printed). **DEV_MODE:** variable is set on `be`, but Railway MCP returns names only, so its literal value was not read. Behavioural proof it is effectively off: `GET https://zarya-production-fe.up.railway.app/api/events` without Telegram init data → `401 {"detail":"Missing Telegram init data"}` (with `DEV_MODE=true` the backend skips auth and returns 200 — `Settings.allow_browser_dev`). **CORS:** request with `Origin: https://evil.example` gets no `access-control-allow-origin` header and preflight returns 400, so `CORS_ORIGINS` is not `*`. **WEBAPP_URL / ADMIN_TELEGRAM_IDS / BOT_TOKEN / SECRET_KEY:** names present on `be`; values unverified. Frontend is served over HTTPS (`200`). Owner by hand: Railway → `zarya-friends` → `be` → Variables: `DEV_MODE` is `false` or empty, `WEBAPP_URL` = `https://zarya-production-fe.up.railway.app`, `CORS_ORIGINS` lists the frontend URL + `https://web.telegram.org`, `SECRET_KEY` is not `change-me-in-production`, `ADMIN_TELEGRAM_IDS` contains your id. |
| 6 | End-to-end run with real Telegram accounts (list → register → cancel → `.ics` → admin `/admin` create/edit) | **unknown** | No recorded e2e run in docs. Runnable script: [Item 6 e2e script](#item-6--e2e-script-live-telegram-accounts). Note date + result under Evidence. |
| 7 | Pilot: invite ~20 users, validate flows | **unknown** | No pilot record found (7-day Railway HTTP stats 2026-11-26: ~5 requests, i.e. no real users yet). Plan, success criteria and go-to-20 gate: [Item 7 pilot plan](#item-7--pilot-plan). Invite text + report instructions: [`pilot-kit.md`](pilot-kit.md). |
| 8 | Triage bugs from the pilot | **unknown** (blocked by 7) | One backlog line per bug in [`tasks.md`](tasks.md#pilot-bugs) using the intake template there; bugfixes skip NMT/DoR. |
| 9 | Optional: Cursor Automation `factory-implement` | **gap (optional)** | Not created. Prompt and operator checklist: [`process/ai-factory/ORCHESTRATOR.md`](../../../process/ai-factory/ORCHESTRATOR.md). Dry-run on one DoR ticket first; no ticket is DoR-ready today (`tasks.md`). |

## After ship (each product change with a user-visible claim)

- [ ] Open a followthrough row in Project store `docs/followthrough/<change-id>.md` (template: [`process/ai-factory/FOLLOWTHROUGH.md`](../../../process/ai-factory/FOLLOWTHROUGH.md)): baseline, expected effect, check-by date, owner. Link that path from the PR and ticket; record the verdict `keep` / `tweak` / `rollback` in the same store file after the check (do not leave the only copy in a closed PR body).

## Item 6 — e2e script (live Telegram accounts)

Owner runs this once, **before inviting friends** (step 2 of the recommended order below). Needs: admin account (your id is in `ADMIN_TELEGRAM_IDS`), one non-admin account (second phone or a trusted friend), prod bot. Do not use `dev-local.sh` with the prod `BOT_TOKEN` while testing (one polling process per token).

Caution: "🔔 Создать и уведомить всех" messages **every** user in the `users` table. Run this script while the table holds only test accounts, or choose "✅ Создать без уведомления" once friends have joined. Name test events `ТЕСТ …` and delete them at the end.

**A. Admin (admin account, bot chat)**

- [ ] `/admin` shows the menu: Создать событие · Управлять событиями · Архив · Написать всем · Написать группе
- [ ] Создать событие: name, date/time ~24 h from now, location, capacity, price, cover image (JPEG/PNG) → confirm with «🔔 Создать и уведомить всех»
- [ ] Управлять событиями → the test event → Редактировать (change location or capacity) → confirm; change is visible in the Mini App

**B. Participant (non-admin account)**

- [ ] `/start` → open the Mini App from the bot (menu button) — list of upcoming events loads, cover images show, UI is in Russian
- [ ] Announcement DM about the new event arrived (from A); its link opens the event card
- [ ] Open the event card → «Записаться» → status becomes registered; admin sees a registration notification (ADR-005) and the person under Участники
- [ ] «В календарь» → `.ics` opens in the system calendar (try iOS and Android if both are available; note which)
- [ ] «Отменить регистрацию» → status resets; admin sees the cancellation; seat is released
- [ ] Register again (needed for the smoke below)

**C. Reminder / announcement / broadcast smoke**

- [ ] Admin: Управлять событиями → test event → «Написать участникам» → send short test text → participant receives it
- [ ] Admin: «📢 Написать всем» → send short test text → participant receives it (only test accounts in `users`)
- [ ] Reminder (ADR-013): with the participant registered and the event 23–25 h away, wait for the hourly scheduler tick (runs 08:00–22:00 Moscow time) → participant gets «Ждем вас уже завтра!» with «Не смогу прийти»; tapping the button cancels the registration
- [ ] Admin: delete the test event(s) (Удалить → Да, удалить)

**D. Close out**

- [ ] Railway `be` logs after the run: no `Traceback` / `CRITICAL`; `fe`/`be` 5xx rate still 0%
- [ ] Record under Evidence for item 6: date, who ran it, iOS/Android/Desktop used, pass/fail per section, links to any bug lines added in [`tasks.md`](tasks.md#pilot-bugs)

## Item 7 — pilot plan

Goal: learn whether real people can find, join and attend an event with zero hand-holding, before widening to ~20. Maps to PRD success metrics (all users can register for at least one event in week 1; bot manages status correctly; admin creates/manages events without friction).

**Preconditions:** item 1 secret set or a manual log check agreed, item 5 values confirmed by the owner, item 6 e2e passed (no open P1 bug in `tasks.md`).

**Wave 1 — 3–5 friends (≈ 1 week)**

1. Pick 3–5 people on mixed devices (at least one iOS and one Android) who will give blunt feedback; at least one has not seen the product.
2. Admin creates **one real upcoming event** (or a clearly labelled test event) and sends the invite text from [`pilot-kit.md`](pilot-kit.md) personally to each friend.
3. Within 48 h ask each friend for one line: "Got confused anywhere?" (reports go to `tasks.md` as pilot bugs). Do not add features in response — log and triage only.
4. Review Railway `be` / `fe` logs and 5xx rate once a day while the wave runs.

**Success criteria for wave 1 (all must hold)**

- [ ] ≥ 80% of invited friends (≥ 3 of 4, or 4 of 5) opened the Mini App and registered for the event with no help from the owner
- [ ] 0 friends reported a lost registration, a wrong status, or a broken cancellation; bot status always matches the Mini App
- [ ] Reminder DM arrived for every registered friend within the expected 23–25 h window (or the miss is explained and fixed)
- [ ] No 5xx bursts and no `Traceback` in `be` logs during the wave (7-day 5xx rate on both services stays ~0%)
- [ ] `.ics` export worked on every friend device that tried it
- [ ] The admin created or edited an event during the wave without needing to touch the DB or Railway

**Go to ~20 only if:** all criteria above are met, **and** every P1 (blocks register / cancel / reminders) pilot bug is fixed and re-verified, **and** the owner confirms item 5 values by hand. P2/P3 bugs may stay open but must be listed in `tasks.md`. Wave 2 repeats the same invite text; keep the same success checks with a target of ≥ 80% of ~20 registering for at least one event within the first week (PRD metric).

**Stop / hold the invite if:** a registration is silently lost, reminders go to the wrong people, 5xx appears in logs, or the bot stops polling (no `Connection established` after errors). Fix first, then restart wave 1.

**Not part of the pilot (needs an ADR first):** access codes, profiles, participant-list visibility, English UI, public web (T-304).

## Order

1 → 5 (owner, short) → 6 → 7 → 8. Item 9 waits until a DoR-ready ticket exists.

## Open questions for the owner

- Is the pilot already informally running (items 6–7 may be done but unrecorded)?
- Should the Railway scan stay a skip-on-missing-token no-op, or become a required gate once the token is set?
