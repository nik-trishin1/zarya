# ADR-001: Technology Stack

**Date:** 2026-06-23
**Status:** Accepted

## Context

zarya is a community event management platform for a small group (~20 people) with a one-week MVP deadline and zero budget. The primary interface must be Telegram-native to minimize onboarding friction for the initial user base, which already communicates via Telegram.

## Decision

The following stack was selected for the MVP:

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Frontend | React 18 + TypeScript + Telegram Web App SDK | Native Telegram Mini App experience; familiar ecosystem; good UX options |
| Backend | FastAPI (Python 3.11) | Fast to develop; async support; auto-generated OpenAPI docs |
| Bot framework | aiogram 3.x | Modern async Python Telegram bot library; well-maintained |
| Database | PostgreSQL | Reliable; Railway-native support; easy to migrate to managed cloud later |
| Deployment | Railway.com | Free tier available; Docker-native; owner already has access |
| Image storage | Railway volume or Cloudinary (free tier) | Cover image uploads for events |

## Alternatives Considered

**SQLite instead of PostgreSQL.** SQLite would be simpler for local development but does not support concurrent writes well and is harder to migrate from. PostgreSQL on Railway is available at no additional cost, so the tradeoff favors PostgreSQL.

**Telegram bot only (no Mini App).** A pure text bot would be faster to build but would severely limit UX quality. The PRD explicitly requires a Mini App for better UX, and the Telegram Web App SDK enables a modern interface within the same Telegram context.

**Next.js instead of React.** Next.js adds SSR complexity that is unnecessary for a client-side Mini App. Plain React with Vite is lighter and faster to iterate on.

## Consequences

The team must maintain a Docker-based deployment on Railway. The frontend is a static SPA served from Railway. The backend exposes a REST API consumed by both the Mini App and the Telegram bot. Future iterations can add a standalone web interface without changing the backend.
