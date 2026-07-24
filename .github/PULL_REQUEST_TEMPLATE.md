# Pull Request Checklist

## Summary

<!-- Plain language: what changes for users/ops and why. Link ticket T-NNN. -->

## Human summary alignment

- [ ] Diff matches the ticket/spec **Human summary** (no silent scope creep)

## Ticket / Spec

- Ticket: `T-` / path:
- Spec / ADR:

## Verification

- [ ] Backend tests pass (`pytest`) — or N/A
- [ ] Frontend `lint` + `build` pass — or N/A
- [ ] CI green (includes Railway log scan when `RAILWAY_TOKEN` is configured)
- [ ] User-facing strings are in Russian; code/comments in English
- [ ] No secrets committed

## Review pass

- [ ] Separate review requested (`process/ai-factory/REVIEW_PASS.md`)
- [ ] Review findings addressed or explicitly deferred with rationale

## Defaults chosen / risks

<!-- Safe defaults picked under factory mode; residual risks -->
