import { useState } from 'react'
import { updateRequest } from '../services/api.js'
import Modal from './Modal.jsx'

export default function AssignTechnicianModal({ request, technicians, onClose, onAssigned }) {
  const [busyId, setBusyId] = useState(null)
  const [error, setError] = useState(null)

  const available = technicians.filter((t) => t.availability === 'Available').length
  const current = request.technician_id

  async function assign(technicianId) {
    setBusyId(technicianId ?? 'none')
    setError(null)
    try {
      const updated = await updateRequest(request.id, { technician_id: technicianId })
      onAssigned(updated)
      onClose()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusyId(null)
    }
  }

  return (
    <Modal title={`Assign technician: request #${request.id}`} onClose={onClose}>
      <p className="assign-summary">
        <span className="strong">{request.title}</span>
        <span className="muted small">
          {' '}· Currently {request.technician_name ? <strong>{request.technician_name}</strong> : 'unassigned'}
        </span>
      </p>
      <p className="muted small assign-count">
        {available} of {technicians.length} technicians available. Only available technicians can be newly assigned.
      </p>

      {error && (
        <div className="form-alert form-alert--error" role="alert">
          {error}
        </div>
      )}

      {technicians.length === 0 ? (
        <p className="muted">No technicians exist yet. Add one on the Technicians page first.</p>
      ) : (
        <ul className="assign-list">
          {technicians.map((technician) => {
            const isCurrent = technician.id === current
            const selectable = technician.availability === 'Available' || isCurrent
            return (
              <li key={technician.id} className={`assign-list__item ${!selectable ? 'is-disabled' : ''}`}>
                <div className="assign-list__main">
                  <span className="strong">{technician.name}</span>
                  <span className="muted small">
                    {technician.specialization} · {technician.active_request_count} active request
                    {technician.active_request_count === 1 ? '' : 's'}
                  </span>
                </div>
                <div className="assign-list__status">
                  <span className={`badge ${technician.availability === 'Available' ? 'badge--available' : 'badge--unavailable'}`}>
                    {technician.availability}
                  </span>
                  {isCurrent ? (
                    <span className="badge badge--open">Assigned</span>
                  ) : (
                    <button
                      type="button"
                      className="btn btn--primary btn--small"
                      disabled={!selectable || busyId !== null}
                      onClick={() => assign(technician.id)}
                      title={selectable ? '' : 'Unavailable technicians cannot be assigned'}
                    >
                      {busyId === technician.id ? 'Assigning...' : 'Assign'}
                    </button>
                  )}
                </div>
              </li>
            )
          })}
        </ul>
      )}

      {current && (
        <div className="assign-footer">
          <button type="button" className="btn btn--ghost btn--danger-text" disabled={busyId !== null} onClick={() => assign(null)}>
            {busyId === 'none' ? 'Removing...' : 'Remove assignment'}
          </button>
        </div>
      )}
    </Modal>
  )
}
