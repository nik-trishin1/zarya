const EVENT_START_PARAM_RE = /^event_(\d+)$/;

export function parseEventStartParam(param: string | null | undefined): number | null {
  if (!param) return null;
  const match = param.match(EVENT_START_PARAM_RE);
  if (!match) return null;
  const eventId = Number(match[1]);
  return Number.isFinite(eventId) && eventId > 0 ? eventId : null;
}

export function getTelegramStartParam(): string | null {
  const fromInit = window.Telegram?.WebApp?.initDataUnsafe?.start_param;
  if (fromInit) return fromInit;
  return new URLSearchParams(window.location.search).get("tgWebAppStartParam");
}

export function getBotUsername(): string {
  const fromEnv = import.meta.env.VITE_BOT_USERNAME?.trim();
  if (fromEnv) return fromEnv.replace(/^@/, "");
  return "zarya_friends_bot";
}

export function buildEventShareLink(eventId: number): string {
  return `https://t.me/${getBotUsername()}?startapp=event_${eventId}`;
}
