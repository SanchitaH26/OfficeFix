// Mirrors backend/app/schemas.py so the form reports the same rules the server enforces.

export const EMAIL_PATTERN = /^[^@\s]+@[^@\s]+\.[^@\s]+$/
export const NAME_PATTERN = /^[\p{L} .'\-]+$/u
export const TEXT_PATTERN = /^[\p{L}\p{N} .,\-()\/&'#]+$/u

export const LIMITS = {
  name: 120,
  email: 254,
  title: 200,
  location: 200,
  description: 5000,
  notes: 5000,
  specialization: 120,
  categoryOther: 100,
}

export function checkName(value, label) {
  const trimmed = value.trim()
  if (!trimmed) return `${label} is required.`
  if (trimmed.length > LIMITS.name) return `${label} must be ${LIMITS.name} characters or fewer.`
  if (!NAME_PATTERN.test(trimmed)) {
    return `${label} may contain only letters, spaces, hyphens (-), apostrophes (') and periods (.).`
  }
  return null
}

export function checkText(value, label, max) {
  const trimmed = value.trim()
  if (!trimmed) return `${label} is required.`
  if (trimmed.length > max) return `${label} must be ${max} characters or fewer.`
  if (!TEXT_PATTERN.test(trimmed)) {
    return `${label} may contain only letters, numbers, spaces and . , - ( ) / & ' #.`
  }
  return null
}

export function checkEmail(value) {
  const trimmed = value.trim()
  if (!trimmed) return 'Email address is required.'
  if (trimmed.length > LIMITS.email) return `Email must be ${LIMITS.email} characters or fewer.`
  if (!EMAIL_PATTERN.test(trimmed)) return 'Enter a valid email address.'
  return null
}
