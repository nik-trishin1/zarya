export function getTelegramWebApp() {
  return window.Telegram?.WebApp;
}

export function getTelegramInitData(): string {
  return getTelegramWebApp()?.initData || "";
}

export function openTelegramShareLink(message: string): boolean {
  const tg = getTelegramWebApp();
  if (typeof tg?.openTelegramLink !== "function") {
    return false;
  }

  // Text-only: Telegram prepends `url` before `text`, which duplicated the deep link
  // (link → title → link → description). Message already has title → link → description.
  const params = new URLSearchParams({ text: message });
  tg.openTelegramLink(`https://t.me/share/url?${params.toString()}`);
  return true;
}

export function toAbsoluteUrl(path: string): string {
  if (path.startsWith("http://") || path.startsWith("https://")) {
    return path;
  }
  return `${window.location.origin}${path.startsWith("/") ? path : `/${path}`}`;
}
