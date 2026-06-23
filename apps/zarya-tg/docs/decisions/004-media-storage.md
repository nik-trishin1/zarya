# ADR 004: Event cover images in PostgreSQL

## Status

Accepted

## Context

Cover images were stored on the container filesystem (`/app/uploads`). Railway redeploys replace the container filesystem, so images disappeared unless a volume was mounted. Many operators missed the volume step or still lost files after infrastructure changes.

## Decision

Store uploaded cover images in PostgreSQL (`media_files` table) and serve them via `GET /media/{id}`.

- New uploads from the Telegram bot save bytes to the database and return `/media/{uuid}` URLs.
- Legacy `/uploads/...` paths remain supported for reading from disk when files still exist.
- Default cover (`/static/default-cover.svg`) is unchanged.

## Consequences

- Images survive backend redeploys without Railway volumes.
- Uses the existing PostgreSQL service (no S3/Cloudinary setup for MVP).
- Database size grows with images (acceptable at community-event scale; 5 MB limit per image).
- Events created before this change with broken `/uploads/...` URLs need a one-time cover re-upload.

## Alternatives considered

| Option | Why not (for now) |
|--------|-------------------|
| Railway volume only | Operational burden; easy to misconfigure; does not help after DB-only recovery |
| S3 / Cloudflare R2 | Extra service, credentials, and cost for MVP |
| Telegram `file_id` only | URLs expire; exposes bot token if stored as public URL |
