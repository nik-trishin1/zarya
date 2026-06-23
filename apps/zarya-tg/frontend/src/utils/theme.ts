export type AppColorScheme = "light" | "dark";

const THEME_COLORS: Record<AppColorScheme, { bg: string; header: string }> = {
  dark: { bg: "#0d0d0d", header: "#0d0d0d" },
  light: { bg: "#f5f0e8", header: "#f5f0e8" },
};

export function resolveColorScheme(): AppColorScheme {
  const scheme = window.Telegram?.WebApp?.colorScheme;
  if (scheme === "light" || scheme === "dark") {
    return scheme;
  }

  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

export function applyAppTheme(scheme?: AppColorScheme): AppColorScheme {
  const resolved = scheme ?? resolveColorScheme();
  document.documentElement.dataset.theme = resolved;

  const colors = THEME_COLORS[resolved];
  const tg = window.Telegram?.WebApp;
  if (tg?.initData) {
    try {
      tg.setHeaderColor(colors.header);
      tg.setBackgroundColor(colors.bg);
    } catch {
      // Ignore when running with a partial Telegram WebApp stub
    }
  }

  return resolved;
}
