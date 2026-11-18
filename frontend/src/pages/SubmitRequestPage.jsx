import { useState } from 'react'
import { CATEGORIES, PRIORITIES, createRequest } from '../services/api.js'
import { LIMITS, checkEmail, checkName, checkText } from '../services/validation.js'
import CharCounter from '../components/CharCounter.jsx'

const EMPTY_FORM = {
  employee_name: '',
  employee_email: '',
  title: '',
  description: '',
  category: '',
  category_other: '',
  location: '',
  priority: 'Medium',
}

function validate(form) {
  const errors = {}
  errors.employee_name = checkName(form.employee_name, 'Your name') || undefined
  errors.employee_email = checkEmail(form.employee_email) || undefined
  errors.title = checkText(form.title, 'Issue title', LIMITS.title) || undefined

  if (!form.description.trim()) errors.description = 'Describe the issue so the technician can act on it.'
  else if (form.description.trim().length > LIMITS.description) errors.description = `Description must be ${LIMITS.description} characters or fewer.`

  if (!form.category) errors.category = 'Select a category.'
  else if (form.category === 'Other') errors.category_other = checkText(form.category_other, 'Other category', LIMITS.categoryOther) || undefined

  errors.location = checkText(form.location, 'Office location or floor', LIMITS.location) || undefined

  if (!PRIORITIES.includes(form.priority)) errors.priority = 'Select a priority.'
  return errors
}

export default function SubmitRequestPage({ onNotify, onNavigate }) {
  const [form, setForm] = useState(EMPTY_FORM)
  const [errors, setErrors] = useState({})
  const [submitting, setSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState(null)
  const [created, setCreated] = useState(null)

  function update(key, value) {
    setForm((current) => ({
      ...current,
      [key]: value,
      ...(key === 'category' && value !== 'Other' ? { category_other: '' } : {}),
    }))
    setErrors((current) => ({ ...current, [key]: undefined }))
    setSubmitError(null)
  }

  async function handleSubmit(event) {
    event.preventDefault()
    const nextErrors = validate(form)
    setErrors(nextErrors)
    if (Object.values(nextErrors).some(Boolean)) return

    setSubmitting(true)
    setSubmitError(null)
    try {
      const payload = {
        employee_name: form.employee_name.trim(),
        employee_email: form.employee_email.trim(),
        title: form.title.trim(),
        description: form.description.trim(),
        category: form.category,
        category_other: form.category === 'Other' ? form.category_other.trim() : null,
        location: form.location.trim(),
        priority: form.priority,
      }
      const saved = await createRequest(payload)
      setCreated(saved)
      setForm(EMPTY_FORM)
      onNotify(`Request #${saved.id} submitted.`)
    } catch (err) {
      setSubmitError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="stack narrow">
      {created && (
        <div className="form-alert form-alert--success" role="status">
          <span>
            Request #{created.id} has been submitted and is now <strong>{created.status}</strong>.
          </span>
          <button type="button" className="btn btn--ghost btn--small" onClick={() => onNavigate('requests')}>
            View requests
          </button>
        </div>
      )}

      <section className="card">
        <header className="card__header">
          <div>
            <h2>New maintenance request</h2>
            <p className="muted small">Fields marked * are required.</p>
          </div>
        </header>

        <form className="form-grid form-grid--padded" onSubmit={handleSubmit} noValidate>
          <Field label="Your name *" error={errors.employee_name} hint="Letters, spaces, hyphens, apostrophes and periods only." counter={form.employee_name.length} max={LIMITS.name}>
            <input className="input" value={form.employee_name} onChange={(e) => update('employee_name', e.target.value)} autoComplete="name" maxLength={LIMITS.name} />
          </Field>

          <Field label="Your email *" error={errors.employee_email} counter={form.employee_email.length} max={LIMITS.email}>
            <input className="input" type="email" value={form.employee_email} onChange={(e) => update('employee_email', e.target.value)} autoComplete="email" maxLength={LIMITS.email} />
          </Field>

          <Field label="Issue title *" error={errors.title} full hint="Letters, numbers and . , - ( ) / & ' # only." counter={form.title.length} max={LIMITS.title}>
            <input className="input" value={form.title} onChange={(e) => update('title', e.target.value)} placeholder="For example: Air conditioning unit making a loud noise" maxLength={LIMITS.title} />
          </Field>

          <Field label="Category *" error={errors.category}>
            <select className="input" value={form.category} onChange={(e) => update('category', e.target.value)}>
              <option value="">Select a category</option>
              {CATEGORIES.map((category) => (
                <option key={category} value={category}>{category}</option>
              ))}
            </select>
          </Field>

          <Field label="Priority *" error={errors.priority}>
            <select className="input" value={form.priority} onChange={(e) => update('priority', e.target.value)}>
              {PRIORITIES.map((priority) => (
                <option key={priority} value={priority}>{priority}</option>
              ))}
            </select>
          </Field>

          {form.category === 'Other' && (
            <Field label="Specify the category *" error={errors.category_other} full hint="Describe the type of issue, for example: Window blinds." counter={form.category_other.length} max={LIMITS.categoryOther}>
              <input className="input" value={form.category_other} onChange={(e) => update('category_other', e.target.value)} maxLength={LIMITS.categoryOther} />
            </Field>
          )}

          <Field label="Office location or floor *" error={errors.location} full hint="Letters, numbers and . , - ( ) / & ' # only." counter={form.location.length} max={LIMITS.location}>
            <input className="input" value={form.location} onChange={(e) => update('location', e.target.value)} placeholder="For example: Floor 3, Meeting Room B" maxLength={LIMITS.location} />
          </Field>

          <Field label="Description *" error={errors.description} full counter={form.description.length} max={LIMITS.description}>
            <textarea className="input textarea" rows={5} value={form.description} onChange={(e) => update('description', e.target.value)} placeholder="What is happening, where, and since when?" maxLength={LIMITS.description} />
          </Field>

          {submitError && (
            <div className="form-alert form-alert--error full" role="alert">
              {submitError}
            </div>
          )}

          <div className="form-actions full">
            <button type="button" className="btn btn--ghost" onClick={() => { setForm(EMPTY_FORM); setErrors({}); setSubmitError(null) }} disabled={submitting}>
              Clear form
            </button>
            <button type="submit" className="btn btn--primary" disabled={submitting}>
              {submitting ? 'Submitting...' : 'Submit request'}
            </button>
          </div>
        </form>
      </section>
    </div>
  )
}

function Field({ label, error, hint, full = false, counter, max, children }) {
  return (
    <label className={`field ${full ? 'field--full' : ''}`}>
      <span className="field__label">{label}</span>
      {children}
      <span className="field__footer">
        <span className="field__messages">
          {error ? <span className="field__error">{error}</span> : hint && <span className="field__hint">{hint}</span>}
        </span>
        {max && <CharCounter length={counter} max={max} />}
      </span>
    </label>
  )
}
