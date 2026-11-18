import { useCallback, useEffect, useState } from 'react'
import { listTechnicians, updateTechnician } from '../services/api.js'
import { formatDate } from '../services/format.js'
import { AvailabilityBadge } from '../components/Badges.jsx'
import { EmptyState, ErrorState, LoadingState } from '../components/StateMessage.jsx'
import TechnicianModal from '../components/TechnicianModal.jsx'

export default function TechniciansPage({ onNotify }) {
  const [technicians, setTechnicians] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [editing, setEditing] = useState(null)
  const [adding, setAdding] = useState(false)
  const [togglingId, setTogglingId] = useState(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      setTechnicians(await listTechnicians())
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  async function toggleAvailability(technician) {
    const next = technician.availability === 'Available' ? 'Unavailable' : 'Available'
    setTogglingId(technician.id)
    try {
      const updated = await updateTechnician(technician.id, { availability: next })
      setTechnicians((current) => current.map((item) => (item.id === updated.id ? updated : item)))
      onNotify(`${updated.name} is now ${updated.availability.toLowerCase()}.`)
    } catch (err) {
      onNotify(err.message, 'error')
    } finally {
      setTogglingId(null)
    }
  }

  function handleSaved(saved, message) {
    setTechnicians((current) => {
      const exists = current.some((item) => item.id === saved.id)
      return exists ? current.map((item) => (item.id === saved.id ? saved : item)) : [...current, saved]
    })
    setEditing(null)
    setAdding(false)
    onNotify(message)
    load()
  }

  return (
    <div className="stack">
      <section className="card">
        <header className="card__header">
          <div>
            <h2>Maintenance team</h2>
            <p className="muted small">Only technicians marked Available can be assigned to new requests.</p>
          </div>
          <button type="button" className="btn btn--primary" onClick={() => setAdding(true)}>
            Add technician
          </button>
        </header>

        {loading && technicians.length === 0 ? (
          <LoadingState label="Loading technicians..." />
        ) : error ? (
          <ErrorState message={error} onRetry={load} />
        ) : technicians.length === 0 ? (
          <EmptyState message="No technicians yet. Add one to start assigning requests." />
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Specialization</th>
                  <th>Availability</th>
                  <th className="num">Active requests</th>
                  <th>Added</th>
                  <th className="actions-col">Actions</th>
                </tr>
              </thead>
              <tbody>
                {technicians.map((technician) => (
                  <tr key={technician.id}>
                    <td className="strong">{technician.name}</td>
                    <td>{technician.email}</td>
                    <td>{technician.specialization}</td>
                    <td><AvailabilityBadge availability={technician.availability} /></td>
                    <td className="num">{technician.active_request_count}</td>
                    <td className="nowrap">{formatDate(technician.created_at)}</td>
                    <td className="actions-col">
                      <button type="button" className="btn btn--ghost btn--small" onClick={() => setEditing(technician)}>
                        Edit
                      </button>
                      <button
                        type="button"
                        className="btn btn--ghost btn--small"
                        onClick={() => toggleAvailability(technician)}
                        disabled={togglingId === technician.id}
                      >
                        {togglingId === technician.id
                          ? 'Updating...'
                          : technician.availability === 'Available'
                            ? 'Mark unavailable'
                            : 'Mark available'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {adding && <TechnicianModal onClose={() => setAdding(false)} onSaved={handleSaved} />}
      {editing && <TechnicianModal technician={editing} onClose={() => setEditing(null)} onSaved={handleSaved} />}
    </div>
  )
}
