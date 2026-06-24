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

export function getBotAppShortName(): string | null {
  const fromEnv = import.meta.env.VITE_BOT_APP_SHORT_NAME?.trim();
  if (!fromEnv) return null;
  return fromEnv.replace(/^@/, "");
}

export function buildEventStartParam(eventId: number): string {
  return `event_${eventId}`;
}

export function buildEventShareLink(eventId: number): string {
  const username = getBotUsername();
  const startParam = buildEventStartParam(eventId);
  const params = new URLSearchParams();
  params.set("startapp", startParam);
  params.set("startApp", startParam);
  const shortName = getBotAppShortName();
  const base = shortName
    ? `https://t.me/${username}/${shortName}`
    : `https://t.me/${username}`;
  return `${base}?${params.toString()}`;
}

export function formatShareMessage(title: string, url: string, description?: string): string {
  const lines = [title.trim(), url.trim()];
  const desc = description?.trim();
  if (desc) {
    lines.push("", desc);
  }
  return lines.join("\n");
}
