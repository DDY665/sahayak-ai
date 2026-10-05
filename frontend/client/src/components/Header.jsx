export default function Header({ theme, onToggleTheme, health, uiText, mobileMenuOpen, onToggleMobileMenu }) {
  const healthy = health?.node === "ok" && health?.python === "ok";
  const text = uiText || {
    dark: "Dark",
    light: "Light",
    toggleTheme: "Toggle theme",
    serverOnline: "Server online",
    serverOffline: "Server offline"
  };

  return (
    <header>
      <div className="header-left">
        <button
          className={`mobile-menu-btn ${mobileMenuOpen ? "active" : ""}`}
          onClick={onToggleMobileMenu}
          aria-label="Toggle navigation sidebar"
          type="button"
        >
          <span className="hamburger-line" />
          <span className="hamburger-line" />
          <span className="hamburger-line" />
        </button>
        <div className="logo"><span className="logo-light">Sahayak</span>AI</div>
      </div>
      <div className="header-actions">
        <div className="theme-controls">
          <span className="theme-label">{theme === "dark" ? text.dark : text.light}</span>
          <button className="theme-toggle" onClick={onToggleTheme} aria-label={text.toggleTheme} type="button" />
        </div>
        <div className="status-badge">
          <div className={`status-dot ${healthy ? "online" : ""}`} />
          <span>{healthy ? text.serverOnline : text.serverOffline}</span>
        </div>
      </div>
    </header>
  );
}
