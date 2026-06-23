import { useEffect } from "react";
import WebApp from "@twa-dev/sdk";

export function useTelegram() {
  useEffect(() => {
    WebApp.ready();
    WebApp.expand();
    WebApp.setHeaderColor("#0D0D0D");
    WebApp.setBackgroundColor("#0D0D0D");
  }, []);

  return WebApp;
}
