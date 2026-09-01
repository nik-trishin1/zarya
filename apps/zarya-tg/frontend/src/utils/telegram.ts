export function getTelegramWebApp() {
  return window.Telegram?.WebApp;
}

export function getTelegramInitData(): string {
  return getTelegramWebApp()?.initData || "";
}

export function hapticImpact(style: "light" | "medium" | "heavy" = "medium"): void {
  const haptic = getTelegramWebApp()?.HapticFeedback;
  if (typeof haptic?.impactOccurred === "function") {
    haptic.impactOccurred(style);
  }
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

function isTelegramHost(url: string): boolean {
  try {
    const host = new URL(url).hostname.toLowerCase();
    return host === "t.me" || host.endsWith(".t.me");
  } catch {
    return false;
  }
}

/** Open an http(s) URL in the system browser; t.me links stay inside Telegram when possible. */
export function openExternalUrl(url: string): void {
  const tg = getTelegramWebApp();
  if (isTelegramHost(url) && typeof tg?.openTelegramLink === "function") {
    tg.openTelegramLink(url);
    return;
  }
  if (typeof tg?.openLink === "function") {
    tg.openLink(url);
    return;
  }
  window.open(url, "_blank", "noopener,noreferrer");
}
