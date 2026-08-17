import { getTelegramWebApp } from "./telegram";

/**
 * Open a pre-filled “add event” screen via HTTPS calendar URL.
 *
 * Telegram WebView cannot open `intent:` / `webcal:` (ERR_UNKNOWN_URL_SCHEME).
 * `downloadFile` shows a .ics save dialog instead of the add-event UI.
 */
export function openPrefilledCalendar(googleUrl: string): void {
  const tg = getTelegramWebApp();
  if (typeof tg?.openLink === "function") {
    tg.openLink(googleUrl);
    return;
  }
  window.open(googleUrl, "_blank", "noopener,noreferrer");
}
