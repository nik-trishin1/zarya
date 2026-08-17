import { getTelegramInitData, getTelegramWebApp } from "./telegram";

export interface CalendarAddPayload {
  title: string;
  description: string;
  location: string;
  begin_ms: number;
  end_ms: number;
}

export function isAndroidUserAgent(ua: string = navigator.userAgent): boolean {
  return /Android/i.test(ua);
}

/** Opens the system calendar insert/edit screen. No https → no in-app browser. */
export function buildAndroidInsertIntent(event: CalendarAddPayload): string {
  const extras = [
    "action=android.intent.action.INSERT",
    "type=vnd.android.cursor.item/event",
    `S.title=${encodeURIComponent(event.title)}`,
    `S.description=${encodeURIComponent(event.description)}`,
    `S.eventLocation=${encodeURIComponent(event.location)}`,
    `l.beginTime=${event.begin_ms}`,
    `l.endTime=${event.end_ms}`,
    "end",
  ];
  return `intent://event#Intent;${extras.join(";")}`;
}

export function hasCalendarInsertPayload(
  value: Partial<CalendarAddPayload>,
): value is CalendarAddPayload {
  return (
    typeof value.title === "string" &&
    typeof value.description === "string" &&
    typeof value.location === "string" &&
    typeof value.begin_ms === "number" &&
    Number.isFinite(value.begin_ms) &&
    typeof value.end_ms === "number" &&
    Number.isFinite(value.end_ms)
  );
}

export function waitForAppSwitch(ms: number): Promise<boolean> {
  return new Promise((resolve) => {
    let settled = false;
    const finish = (opened: boolean) => {
      if (settled) return;
      settled = true;
      document.removeEventListener("visibilitychange", onVisibility);
      window.removeEventListener("pagehide", onHide);
      window.removeEventListener("blur", onHide);
      window.clearTimeout(timer);
      resolve(opened);
    };
    const onHide = () => finish(true);
    const onVisibility = () => {
      if (document.hidden) finish(true);
    };
    document.addEventListener("visibilitychange", onVisibility);
    window.addEventListener("pagehide", onHide);
    window.addEventListener("blur", onHide);
    const timer = window.setTimeout(() => finish(false), ms);
  });
}

export function openAndroidCalendarInsert(event: CalendarAddPayload): void {
  const intentUrl = buildAndroidInsertIntent(event);
  const anchor = document.createElement("a");
  anchor.href = intentUrl;
  anchor.rel = "noopener";
  anchor.style.display = "none";
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
}

export async function openIcsWithoutBrowser(url: string, fileName: string): Promise<void> {
  const tg = getTelegramWebApp();
  const inTelegram = Boolean(getTelegramInitData());

  if (inTelegram && typeof tg?.downloadFile === "function") {
    const accepted = await new Promise<boolean>((resolve) => {
      try {
        tg.downloadFile!({ url, file_name: fileName }, (ok) => resolve(Boolean(ok)));
      } catch {
        resolve(false);
      }
    });
    if (accepted) return;
    throw new Error("Скачивание отменено");
  }

  if (inTelegram && typeof tg?.openLink === "function") {
    tg.openLink(url);
    return;
  }

  window.location.assign(url);
}
