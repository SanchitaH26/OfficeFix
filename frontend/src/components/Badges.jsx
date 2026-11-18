const STATUS_CLASS = {
  Open: 'badge--open',
  'In Progress': 'badge--progress',
  Resolved: 'badge--resolved',
}

const PRIORITY_CLASS = {
  Low: 'badge--low',
  Medium: 'badge--medium',
  High: 'badge--high',
}

const AVAILABILITY_CLASS = {
  Available: 'badge--available',
  Unavailable: 'badge--unavailable',
}

export function StatusBadge({ status }) {
  return <span className={`badge ${STATUS_CLASS[status] || ''}`}>{status}</span>
}

export function PriorityBadge({ priority }) {
  return <span className={`badge ${PRIORITY_CLASS[priority] || ''}`}>{priority}</span>
}

export function AvailabilityBadge({ availability }) {
  return <span className={`badge ${AVAILABILITY_CLASS[availability] || ''}`}>{availability}</span>
}
