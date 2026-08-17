import { getTelegramInitData, getTelegramWebApp } from "./telegram";

/**
 * Open an HTTPS .ics file without custom URL schemes.
 *
 * Telegram's WebView rejects `intent:` / `webcal:` with ERR_UNKNOWN_URL_SCHEME.
 * Do not use `openLink()` either — that opens the in-app browser.
 */
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

  const shareResult = await tryShareIcsFile(url, fileName);
  if (shareResult === "shared" || shareResult === "cancelled") return;

  await downloadIcsAsFile(url, fileName);
}

async function tryShareIcsFile(
  url: string,
  fileName: string,
): Promise<"shared" | "cancelled" | "unavailable"> {
  if (typeof navigator.share !== "function" || typeof navigator.canShare !== "function") {
    return "unavailable";
  }

  try {
    const response = await fetch(url);
    if (!response.ok) return "unavailable";
    const blob = await response.blob();
    const file = new File([blob], fileName, { type: "text/calendar" });
    if (!navigator.canShare({ files: [file] })) return "unavailable";
    await navigator.share({ files: [file], title: fileName });
    return "shared";
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") {
      return "cancelled";
    }
    return "unavailable";
  }
}

async function downloadIcsAsFile(url: string, fileName: string): Promise<void> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error("Не удалось открыть календарь");
  }
  const blob = await response.blob();
  const objectUrl = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = objectUrl;
  anchor.download = fileName;
  anchor.rel = "noopener";
  anchor.style.display = "none";
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  window.setTimeout(() => URL.revokeObjectURL(objectUrl), 1_000);
}
