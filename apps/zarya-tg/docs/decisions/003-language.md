# ADR-003: Language and Localization

**Date:** 2026-06-23
**Status:** Accepted

## Context

The initial user base of ~20 people is Russian-speaking. The product owner wants to keep the MVP focused and avoid localization overhead.

## Decision

The MVP ships with a Russian-only user interface. All UI text, bot messages, error messages, and calendar exports are in Russian. Code, comments, commit messages, and documentation are in English.

Localization infrastructure (i18n library, translation keys) is deliberately excluded from the MVP to avoid premature abstraction. If English or other languages are needed in Iteration 2, the strings will be extracted and an i18n library (e.g., react-i18next) will be added at that point.

## Consequences

Adding a second language in Iteration 2 will require a one-time refactor to extract all hardcoded Russian strings into translation keys. This is an accepted tradeoff for faster MVP delivery.
