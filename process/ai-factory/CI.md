# CI expectations (portable)

Minimum gates before a factory ticket can be `done`.

## Required on every PR

1. **Automated tests** for the touched backend/services layer (e.g. `pytest`).
2. **Lint + production build** for the touched frontend/app layer.
3. **PR template** checklist filled (ticket link, verification, review pass).

## Railway runtime log scan (recommended)

When the project deploys on Railway, CI should also **pull recent deploy (and optionally HTTP) logs** and fail on error signatures. This catches production/staging breakage that unit tests miss.

### Script

[`scripts/check-railway-logs.sh`](scripts/check-railway-logs.sh)

### GitHub Actions secrets / vars

| Name | Type | Purpose |
|------|------|---------|
| `RAILWAY_TOKEN` | secret | Project token (Settings → Tokens) |
| `RAILWAY_SERVICE_NAMES` | variable | Comma-separated service names, e.g. `zarya-backend,zarya-frontend` |
| `RAILWAY_ENVIRONMENT` | variable | Optional; default `production` |
| `RAILWAY_PROJECT_ID` | variable | Optional; pass if the token is not enough alone |
| `RAILWAY_LOG_LINES` | variable | Optional; default `200` |

If `RAILWAY_TOKEN` is missing, the job **skips successfully** and prints a notice (local forks stay green). When the token is present, the job **fails** on matched error patterns.

### Error patterns (default)

- `Traceback`
- `ERROR` / `CRITICAL` (log levels)
- `Unhandled` / `Exception`
- HTTP 5xx bursts via `railway logs --http --status ">=500"` when HTTP logs are enabled

Projects may override `RAILWAY_ERROR_GREP` (extended regex).

### Example job fragment

```yaml
  railway-logs:
    name: Railway runtime logs
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Scan Railway logs
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
          RAILWAY_SERVICE_NAMES: ${{ vars.RAILWAY_SERVICE_NAMES }}
          RAILWAY_ENVIRONMENT: ${{ vars.RAILWAY_ENVIRONMENT }}
          RAILWAY_PROJECT_ID: ${{ vars.RAILWAY_PROJECT_ID }}
          RAILWAY_LOG_LINES: ${{ vars.RAILWAY_LOG_LINES }}
        run: bash process/ai-factory/scripts/check-railway-logs.sh
```

## Agent rule

Do not mark a ticket `done` while any required CI job is red. Investigate Railway log failures before retrying blindly.
