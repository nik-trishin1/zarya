import "./Header.css";

interface HeaderProps {
  showHomeIcon: boolean;
  onNavClick: () => void;
}

export function Header({ showHomeIcon, onNavClick }: HeaderProps) {
  return (
    <header className="header">
      <button type="button" className="header__nav-btn" onClick={onNavClick} aria-label={showHomeIcon ? "На главную" : "Мои регистрации"}>
        {showHomeIcon ? "🏠" : "🎫"}
      </button>
      <h1 className="header__title">zarya + friends 🌅</h1>
    </header>
  );
}
