export function LoadingState({ label = 'Loading...' }) {
  return (
    <div className="state state--loading" role="status">
      <span className="spinner" aria-hidden="true" />
      <span>{label}</span>
    </div>
  )
}

export function ErrorState({ message, onRetry }) {
  return (
    <div className="state state--error" role="alert">
      <span>{message}</span>
      {onRetry && (
        <button type="button" className="btn btn--ghost btn--small" onClick={onRetry}>
          Try again
        </button>
      )}
    </div>
  )
}

export function EmptyState({ message }) {
  return <div className="state state--empty">{message}</div>
}
