# zarya-tg — Telegram Mini App

The Telegram Mini App for zarya community event management.

## Overview

zarya-tg is a Telegram Mini App that allows community members to browse upcoming events, register, and export events to their calendar — all without leaving Telegram.

## Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + TypeScript + Telegram Web App SDK |
| Backend | FastAPI (Python 3.11) + aiogram 3.x |
| Database | PostgreSQL |
| Deployment | Railway.com (Docker) |

## Structure

```
zarya-tg/
├── frontend/          # React Telegram Mini App
├── backend/           # FastAPI + aiogram bot
└── docs/
    ├── prd.md         # Product Requirements Document (source of truth)
    ├── tasks.md       # Task backlog
    ├── ux_ui_analysis.md
    ├── decisions/     # Architecture Decision Records
    ├── deliverables/  # UI mockups
    ├── research/
    └── assets/
```

## Documentation

- [PRD](docs/prd.md) — full product requirements
- [Tasks](docs/tasks.md) — current backlog
- [UX/UI Analysis](docs/ux_ui_analysis.md) — benchmark analysis and design system
- [ADR-001: Stack](docs/decisions/001-stack.md)
- [ADR-002: Navigation](docs/decisions/002-ux-navigation.md)
- [ADR-003: Language](docs/decisions/003-language.md)

## Getting Started

*Local development setup will be added in Phase 1.*
