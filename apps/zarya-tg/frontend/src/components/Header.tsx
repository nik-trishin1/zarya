import { HomeIcon, TicketIcon } from "./HeaderIcons";
import "./Header.css";

export type HeaderScreen = "home" | "registrations";

interface HeaderProps {
  screen: HeaderScreen;
  registrationCount: number;
  onNavClick: () => void;
}

const TITLES: Record<HeaderScreen, string> = {
  home: "Дом",
  registrations: "Мои регистрации",
};

export function Header({ screen, registrationCount, onNavClick }: HeaderProps) {
  const isHome = screen === "home";
  const navLabel = isHome
    ? `Мои регистрации${registrationCount > 0 ? `, ${registrationCount}` : ""}`
    : "Дом";

  return (
    <header className="header">
      <h1 className="header__title">{TITLES[screen]}</h1>
      <button type="button" className="header__pill" onClick={onNavClick} aria-label={navLabel}>
        {isHome ? (
          <>
            <TicketIcon className="header__pill-icon" />
            <span className="header__pill-count">{registrationCount}</span>
          </>
        ) : (
          <HomeIcon className="header__pill-icon" />
        )}
      </button>
    </header>
  );
}
