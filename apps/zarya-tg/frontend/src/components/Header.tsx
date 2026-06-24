import "./Header.css";

export type HeaderScreen = "home" | "registrations";

interface HeaderProps {
  screen: HeaderScreen;
  registrationCount: number;
  onNavClick: () => void;
}

const TITLES: Record<HeaderScreen, string> = {
  home: "События",
  registrations: "Мои регистрации",
};

export function Header({ screen, registrationCount, onNavClick }: HeaderProps) {
  const isHome = screen === "home";
  const navLabel = isHome
    ? `Мои регистрации${registrationCount > 0 ? `, ${registrationCount}` : ""}`
    : "События";

  return (
    <header className="header">
      <h1 className="header__title">{TITLES[screen]}</h1>
      <button type="button" className="header__pill" onClick={onNavClick} aria-label={navLabel}>
        {isHome ? (
          <>
            <span className="header__pill-emoji" aria-hidden="true">
              🎫
            </span>
            <span className="header__pill-count">{registrationCount}</span>
          </>
        ) : (
          <span className="header__pill-emoji" aria-hidden="true">
            🏠
          </span>
        )}
      </button>
    </header>
  );
}
