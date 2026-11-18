export default function Topbar({ title, subtitle, onToggleNav }) {
  return (
    <header className="topbar">
      <button type="button" className="topbar__menu" onClick={onToggleNav} aria-label="Toggle navigation">
        <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true">
          <path d="M3 6h18M3 12h18M3 18h18" />
        </svg>
      </button>
      <div className="topbar__heading">
        <h1 className="topbar__title">{title}</h1>
        <p className="topbar__subtitle">{subtitle}</p>
      </div>
    </header>
  )
}
