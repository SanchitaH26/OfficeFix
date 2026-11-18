import { PAGES } from '../App.jsx'

const ICONS = {
  dashboard: 'M3 3h7v9H3zM14 3h7v5h-7zM14 12h7v9h-7zM3 16h7v5H3z',
  requests: 'M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2M9 5a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2M9 5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2',
  submit: 'M12 5v14M5 12h14',
  technicians: 'M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75',
}

export default function Sidebar({ activePage, open, onNavigate, onClose }) {
  return (
    <aside className={`sidebar ${open ? 'sidebar--open' : ''}`} aria-label="Main navigation">
      <div className="sidebar__brand">
        <span className="sidebar__logo">OF</span>
        <div>
          <div className="sidebar__title">OfficeFix</div>
          <div className="sidebar__subtitle">Maintenance Management</div>
        </div>
      </div>
      <nav className="sidebar__nav">
        {Object.entries(PAGES).map(([key, page]) => (
          <button
            key={key}
            type="button"
            className={`sidebar__link ${activePage === key ? 'sidebar__link--active' : ''}`}
            onClick={() => {
              onNavigate(key)
              onClose()
            }}
            aria-current={activePage === key ? 'page' : undefined}
          >
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d={ICONS[key]} />
            </svg>
            <span>{page.label}</span>
          </button>
        ))}
      </nav>
      <div className="sidebar__footer">Internal use only</div>
    </aside>
  )
}
