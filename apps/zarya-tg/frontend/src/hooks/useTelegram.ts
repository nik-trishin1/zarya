import { useEffect } from "react";
import WebApp from "@twa-dev/sdk";

function isTelegramWebApp(): boolean {
  return Boolean(window.Telegram?.WebApp?.initData);
}

export function useTelegram() {
  useEffect(() => {
    if (!isTelegramWebApp()) {
      return;
    }
    try {
      WebApp.ready();
      WebApp.expand();
      WebApp.setHeaderColor("#0D0D0D");
      WebApp.setBackgroundColor("#0D0D0D");
    } catch {
      // Running outside Telegram Mini App (e.g. local browser dev)
    }
  }, []);

  return WebApp;
}
