import { useCallback, useEffect, useState } from 'react'
import { getDashboardStats } from '../services/api.js'
import { formatDateTime } from '../services/format.js'
import { AvailabilityBadge, PriorityBadge, StatusBadge } from '../components/Badges.jsx'
import { EmptyState, ErrorState, LoadingState } from '../components/StateMessage.jsx'

const CARDS = [
  { key: 'total_requests', label: 'Total requests', tone: 'neutral', page: 'requests' },
  { key: 'open_requests', label: 'Open', tone: 'open', page: 'requests' },
  { key: 'in_progress_requests', label: 'In progress', tone: 'progress', page: 'requests' },
  { key: 'resolved_requests', label: 'Resolved', tone: 'resolved', page: 'requests' },
  { key: 'high_priority_unresolved', label: 'High priority unresolved', tone: 'high', page: 'requests' },
  { key: 'total_technicians', label: 'Technicians', tone: 'neutral', page: 'technicians' },
  { key: 'available_technicians', label: 'Available technicians', tone: 'resolved', page: 'technicians' },
]

export default function DashboardPage({ onNavigate }) {
  const [stats, setStats] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      setStats(await getDashboardStats())
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  if (loading && !stats) return <LoadingState label="Loading dashboard..." />
  if (error && !stats) return <ErrorState message={error} onRetry={load} />

  return (
    <div className="stack">
      {error && <ErrorState message={error} onRetry={load} />}

      <section className="card-grid" aria-label="Summary">
        {CARDS.map((card) => (
          <button
            key={card.key}
            type="button"
            className={`stat-card stat-card--${card.tone}`}
            onClick={() => onNavigate(card.page)}
          >
            <span className="stat-card__label">{card.label}</span>
            <span className="stat-card__value">{stats[card.key]}</span>
          </button>
        ))}
      </section>

      <div className="two-column">
        <section className="card">
          <header className="card__header">
            <h2>Recently submitted</h2>
            <button type="button" className="btn btn--ghost btn--small" onClick={() => onNavigate('requests')}>
              View all
            </button>
          </header>
          {stats.recent_requests.length === 0 ? (
            <EmptyState message="No maintenance requests have been submitted yet." />
          ) : (
            <ul className="list">
              {stats.recent_requests.map((request) => (
                <li key={request.id} className="list__item">
                  <div className="list__main">
                    <span className="list__title">
                      #{request.id} {request.title}
                    </span>
                    <span className="list__meta">
                      {request.location} · {formatDateTime(request.created_at)}
                    </span>
                  </div>
                  <div className="list__badges">
                    <PriorityBadge priority={request.priority} />
                    <StatusBadge status={request.status} />
                  </div>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="card">
          <header className="card__header">
            <h2>Technician workload</h2>
          </header>
          {stats.technician_workload.length === 0 ? (
            <EmptyState message="No technicians have been added yet." />
          ) : (
            <table className="table table--compact">
              <thead>
                <tr>
                  <th>Technician</th>
                  <th>Availability</th>
                  <th className="num">Active requests</th>
                </tr>
              </thead>
              <tbody>
                {stats.technician_workload.map((row) => (
                  <tr key={row.technician_id}>
                    <td>{row.name}</td>
                    <td>
                      <AvailabilityBadge availability={row.availability} />
                    </td>
                    <td className="num">{row.active_requests}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
      </div>
    </div>
  )
}
