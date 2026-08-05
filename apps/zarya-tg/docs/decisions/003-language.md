# ADR-003: Language and Localization

**Date:** 2026-06-23
**Status:** Accepted
**Updated:** 2026-08-05 — English localization (T-205) cancelled; Russian-only remains standing policy

## Context

The initial user base of ~20 people is Russian-speaking. The product owner wants to keep the product focused and avoid localization overhead.

## Decision

The product ships with a Russian-only user interface. All UI text, bot messages, error messages, and calendar exports are in Russian. Code, comments, commit messages, and documentation are in English.

Localization infrastructure (i18n library, translation keys) is deliberately excluded. Ticket **T-205** (English locale) was cancelled: do not add English UI or an i18n layer unless a new ADR reopens multi-language support.

## Consequences

Hardcoded Russian strings stay in the Mini App and bot. Reopening English later would require extracting strings into translation keys and a new ADR/ticket.
