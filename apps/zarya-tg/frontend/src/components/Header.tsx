import "./Header.css";

interface HeaderProps {
  title: string;
  navLabel: string;
  navIcon: string;
  onNavClick: () => void;
}

export function Header({ title, navLabel, navIcon, onNavClick }: HeaderProps) {
  return (
    <header className="header">
      <h1 className="header__title">{title}</h1>
      <button type="button" className="header__nav" onClick={onNavClick} aria-label={navLabel}>
        <span className="header__nav-icon" aria-hidden="true">
          {navIcon}
        </span>
        <span className="header__nav-label">{navLabel}</span>
      </button>
    </header>
  );
}
