export function getTelegramWebApp() {
  return window.Telegram?.WebApp;
}

export function getTelegramInitData(): string {
  return getTelegramWebApp()?.initData || "";
}

export function openTelegramShareLink(url: string, message: string): boolean {
  const tg = getTelegramWebApp();
  if (typeof tg?.openTelegramLink !== "function") {
    return false;
  }

  // url param keeps native t.me handling on tap (iOS). text carries title → link → description.
  const params = new URLSearchParams({ url, text: message });
  tg.openTelegramLink(`https://t.me/share/url?${params.toString()}`);
  return true;
}

export function toAbsoluteUrl(path: string): string {
  if (path.startsWith("http://") || path.startsWith("https://")) {
    return path;
  }
  return `${window.location.origin}${path.startsWith("/") ? path : `/${path}`}`;
}
