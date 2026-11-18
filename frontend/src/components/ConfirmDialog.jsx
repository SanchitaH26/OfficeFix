import Modal from './Modal.jsx'

export default function ConfirmDialog({ title, message, confirmLabel = 'Confirm', busy = false, onConfirm, onCancel }) {
  return (
    <Modal
      title={title}
      onClose={onCancel}
      footer={
        <>
          <button type="button" className="btn btn--ghost" onClick={onCancel} disabled={busy}>
            Cancel
          </button>
          <button type="button" className="btn btn--danger" onClick={onConfirm} disabled={busy}>
            {busy ? 'Deleting...' : confirmLabel}
          </button>
        </>
      }
    >
      <p className="confirm-text">{message}</p>
    </Modal>
  )
}
