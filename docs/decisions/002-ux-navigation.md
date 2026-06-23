# ADR-002: UX Navigation Pattern

**Date:** 2026-06-23
**Status:** Accepted

## Context

The Mini App needs a navigation pattern that minimizes the number of taps to reach the core user action (event registration). The app has two primary screens: the event list (home) and the user's registrations.

## Decision

The app uses a single-icon toggle navigation instead of a bottom tab bar.

The home screen opens directly to the full event list — no splash screen or intermediate menu. A single icon in the top-left corner serves as the only navigation element: it shows 🎫 on the home screen (tapping navigates to "My Registrations") and shows 🏠 on the registrations screen (tapping returns home). This eliminates the bottom tab bar, which would consume ~50px of vertical space on mobile.

The critical path to registration is two taps: open app → tap event card → tap "Зарегистрироваться".

## Alternatives Considered

**Bottom tab bar.** Standard mobile pattern but wastes vertical space and adds visual weight for an app with only two screens.

**Hamburger menu.** Hides navigation, increases cognitive load, and adds a tap to reach "My Registrations".

## Consequences

The icon toggle is a non-standard pattern and must be clearly communicated to users on first use. A brief tooltip or label on first open may be added in Iteration 2. The pattern scales poorly beyond two screens — if more screens are added, a bottom tab bar or drawer should be reconsidered.
