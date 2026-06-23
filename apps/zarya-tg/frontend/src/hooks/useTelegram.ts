import { useEffect } from "react";
import WebApp from "@twa-dev/sdk";
import { applyAppTheme } from "../utils/theme";

function isTelegramWebApp(): boolean {
  return Boolean(window.Telegram?.WebApp?.initData);
}

function applySafeAreaInsets(): void {
  const root = document.documentElement;
  const { safeAreaInset, contentSafeAreaInset } = WebApp;

  root.style.setProperty("--tg-safe-area-inset-top", `${safeAreaInset.top}px`);
  root.style.setProperty("--tg-safe-area-inset-bottom", `${safeAreaInset.bottom}px`);
  root.style.setProperty("--tg-safe-area-inset-left", `${safeAreaInset.left}px`);
  root.style.setProperty("--tg-safe-area-inset-right", `${safeAreaInset.right}px`);
  root.style.setProperty("--tg-content-safe-area-inset-top", `${contentSafeAreaInset.top}px`);
  root.style.setProperty("--tg-content-safe-area-inset-bottom", `${contentSafeAreaInset.bottom}px`);
  root.style.setProperty("--tg-content-safe-area-inset-left", `${contentSafeAreaInset.left}px`);
  root.style.setProperty("--tg-content-safe-area-inset-right", `${contentSafeAreaInset.right}px`);
}

export function useTelegram() {
  useEffect(() => {
    applyAppTheme();

    if (!isTelegramWebApp()) {
      const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
      const onSystemThemeChange = () => {
        applyAppTheme();
      };
      mediaQuery.addEventListener("change", onSystemThemeChange);
      return () => mediaQuery.removeEventListener("change", onSystemThemeChange);
    }

    try {
      WebApp.ready();
      WebApp.expand();
      applyAppTheme();

      if (typeof WebApp.requestFullscreen === "function") {
        WebApp.requestFullscreen();
      }

      const onThemeChanged = () => {
        applyAppTheme();
      };

      applySafeAreaInsets();
      WebApp.onEvent("safeAreaChanged", applySafeAreaInsets);
      WebApp.onEvent("contentSafeAreaChanged", applySafeAreaInsets);
      WebApp.onEvent("themeChanged", onThemeChanged);

      return () => {
        WebApp.offEvent("safeAreaChanged", applySafeAreaInsets);
        WebApp.offEvent("contentSafeAreaChanged", applySafeAreaInsets);
        WebApp.offEvent("themeChanged", onThemeChanged);
      };
    } catch {
      // Running outside Telegram Mini App (e.g. local browser dev)
    }
  }, []);

  return WebApp;
}
