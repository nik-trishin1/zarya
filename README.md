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
├── process/           # Portable AI-Factory standards (reuse in other repos)
├── apps/
│   └── zarya-tg/      # Telegram Mini App
├── .cursor/
│   └── rules/         # Cursor AI behavior rules
├── .github/
│   └── workflows/     # CI (pytest, lint/build, Railway log scan)
└── .gitignore
```

## AI-Factory process

Cross-project playbook: [process/README.md](process/README.md).  
zarya-tg tickets: [apps/zarya-tg/docs/tickets/](apps/zarya-tg/docs/tickets/).

## Contributing

See [AGENTS.md](AGENTS.md) for AI agent instructions and repository conventions.
