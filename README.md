# zarya 🌅

A community platform for organizing and attending social events — built around a home as a gathering place, starting with a close circle of friends.

## Apps

| App | Description | Stack |
|-----|-------------|-------|
| [zarya-tg](apps/zarya-tg/) | Telegram Mini App (MVP) | React + FastAPI + PostgreSQL |

## Repository Structure

```
zarya/
├── AGENTS.md          # AI agent instructions (read first)
├── process/           # Portable AI-Factory + Next Move Theory wiring
├── apps/
│   └── zarya-tg/      # Telegram Mini App
├── Next-Move-Theory-Canon/  # Vendored AJTBD / NMT theses
├── .cursor/
│   ├── rules/         # Cursor AI behavior rules
│   └── skills/        # product-hypothesis + nmt-* skills
├── .github/
│   └── workflows/     # CI (pytest, lint/build, Railway log scan)
└── .gitignore
```

## AI-Factory process

Cross-project playbook: [process/README.md](process/README.md).  
zarya-tg tickets: [apps/zarya-tg/docs/tickets/](apps/zarya-tg/docs/tickets/).

Large product hypotheses (what to build, who for, whether the bet should live) go through **Next Move Theory** before specs or code. Start with the Cursor skill `product-hypothesis`. Canon, skills, and update steps: [process/next-move-theory/README.md](process/next-move-theory/README.md). Upstream: [Next Move Theory Canon and Skills](https://github.com/zamesin/Next-Move-Theory-Canon-and-Skills) (CC BY-NC-SA 4.0).

## Contributing

See [AGENTS.md](AGENTS.md) for AI agent instructions and repository conventions.
