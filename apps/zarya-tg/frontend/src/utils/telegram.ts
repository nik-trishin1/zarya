export function getTelegramWebApp() {
  return window.Telegram?.WebApp;
}

export function getTelegramInitData(): string {
  return getTelegramWebApp()?.initData || "";
}

export function openTelegramShareLink(url: string, title: string): boolean {
  const tg = getTelegramWebApp();
  if (typeof tg?.openTelegramLink !== "function") {
    return false;
  }

  // Pass url separately so Telegram treats it as a native t.me deep link (important on iOS).
  const params = new URLSearchParams({ url, text: title });
  tg.openTelegramLink(`https://t.me/share/url?${params.toString()}`);
  return true;
}

export function formatShareMessage(title: string, url: string): string {
  return `${title}\n${url}`;
}

export function toAbsoluteUrl(path: string): string {
  if (path.startsWith("http://") || path.startsWith("https://")) {
    return path;
  }
  return `${window.location.origin}${path.startsWith("/") ? path : `/${path}`}`;
}
