export function getTelegramWebApp() {
  return window.Telegram?.WebApp;
}

export function getTelegramInitData(): string {
  return getTelegramWebApp()?.initData || "";
}

export function openTelegramShareLink(url: string, message?: string): boolean {
  const tg = getTelegramWebApp();
  if (typeof tg?.openTelegramLink !== "function") {
    return false;
  }

  const shareUrl = message
    ? `https://t.me/share/url?url=${encodeURIComponent(url)}&text=${encodeURIComponent(message)}`
    : url;
  tg.openTelegramLink(shareUrl);
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
