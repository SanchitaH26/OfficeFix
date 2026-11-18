import { useCallback, useEffect, useState } from 'react'
import Sidebar from './components/Sidebar.jsx'
import Topbar from './components/Topbar.jsx'
import Toast from './components/Toast.jsx'
import DashboardPage from './pages/DashboardPage.jsx'
import RequestsPage from './pages/RequestsPage.jsx'
import SubmitRequestPage from './pages/SubmitRequestPage.jsx'
import TechniciansPage from './pages/TechniciansPage.jsx'

export const PAGES = {
  dashboard: { label: 'Dashboard', title: 'Dashboard', subtitle: 'Live maintenance overview' },
  requests: { label: 'Maintenance Requests', title: 'Maintenance Requests', subtitle: 'Review, assign and resolve office issues' },
  submit: { label: 'Submit Request', title: 'Submit Maintenance Request', subtitle: 'Report an office issue to the facilities team' },
  technicians: { label: 'Technicians', title: 'Technicians', subtitle: 'Manage maintenance staff and availability' },
}

function currentPageFromHash() {
  const key = window.location.hash.replace(/^#\/?/, '')
  return PAGES[key] ? key : 'dashboard'
}

export default function App() {
  const [page, setPage] = useState(currentPageFromHash)
  const [navOpen, setNavOpen] = useState(false)
  const [toast, setToast] = useState(null)

  useEffect(() => {
    const onHashChange = () => {
      setPage(currentPageFromHash())
      setNavOpen(false)
    }
    window.addEventListener('hashchange', onHashChange)
    return () => window.removeEventListener('hashchange', onHashChange)
  }, [])

  const notify = useCallback((message, type = 'success') => {
    setToast({ id: Date.now(), message, type })
  }, [])

  const dismissToast = useCallback(() => setToast(null), [])

  const navigate = useCallback((key) => {
    window.location.hash = `/${key}`
  }, [])

  const current = PAGES[page]

  let content
  if (page === 'dashboard') content = <DashboardPage onNavigate={navigate} />
  else if (page === 'requests') content = <RequestsPage onNotify={notify} />
  else if (page === 'submit') content = <SubmitRequestPage onNotify={notify} onNavigate={navigate} />
  else content = <TechniciansPage onNotify={notify} />

  return (
    <div className="app-shell">
      <Sidebar
        activePage={page}
        open={navOpen}
        onNavigate={navigate}
        onClose={() => setNavOpen(false)}
      />
      {navOpen && <div className="sidebar-backdrop" onClick={() => setNavOpen(false)} aria-hidden="true" />}
      <div className="app-main">
        <Topbar
          title={current.title}
          subtitle={current.subtitle}
          onToggleNav={() => setNavOpen((open) => !open)}
        />
        <main className="page-content" key={page}>
          {content}
        </main>
      </div>
      <Toast toast={toast} onDismiss={dismissToast} />
    </div>
  )
}
