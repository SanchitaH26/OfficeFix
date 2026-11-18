import axios from 'axios'

export const CATEGORIES = ['Electrical', 'HVAC/AC', 'Plumbing', 'Internet/Network', 'Furniture', 'Other']
export const PRIORITIES = ['Low', 'Medium', 'High']
export const STATUSES = ['Open', 'In Progress', 'Resolved']
export const AVAILABILITIES = ['Available', 'Unavailable']

const DEFAULT_API_BASE_URL = 'http://localhost:8001'
const API_PREFIX = '/api/v1'

// Remove every trailing slash so the base URL never produces "//" when joined with an endpoint.
const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || DEFAULT_API_BASE_URL).replace(/\/+$/, '')

const http = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: { Accept: 'application/json' },
})

// Every endpoint is written with exactly one leading slash, and joined to the prefix in one place.
function route(endpoint) {
  return `${API_PREFIX}/${endpoint.replace(/^\/+/, '')}`
}

const FIELD_LABELS = {
  employee_name: 'Employee name',
  employee_email: 'Employee email',
  title: 'Issue title',
  description: 'Description',
  category: 'Category',
  category_other: 'Other category',
  location: 'Location',
  priority: 'Priority',
  status: 'Status',
  technician_id: 'Technician',
  resolution_notes: 'Resolution notes',
  name: 'Name',
  email: 'Email',
  specialization: 'Specialization',
  availability: 'Availability',
}

function describeValidationError(item) {
  const field = Array.isArray(item.loc) ? item.loc[item.loc.length - 1] : undefined
  const label = FIELD_LABELS[field] || field || 'Input'
  if (item.type === 'string_pattern_mismatch') {
    if (field?.includes('email')) return `${label} must be a valid email address.`
    if (field === 'employee_name' || field === 'name') {
      return `${label} may contain only letters, spaces, hyphens (-), apostrophes (') and periods (.).`
    }
    return `${label} may contain only letters, numbers, spaces and . , - ( ) / & ' #.`
  }
  if (item.type === 'string_too_short' || item.type === 'missing') {
    return `${label} is required.`
  }
  return `${label}: ${item.msg}`
}

export class ApiError extends Error {
  constructor(message, status) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

function toApiError(error) {
  if (error.response) {
    const { status, data } = error.response
    const detail = data?.detail
    if (typeof detail === 'string') {
      return new ApiError(detail, status)
    }
    if (Array.isArray(detail) && detail.length > 0) {
      return new ApiError(detail.map(describeValidationError).join(' '), status)
    }
    return new ApiError(`The server returned an unexpected error (HTTP ${status}).`, status)
  }
  if (error.request) {
    return new ApiError(
      `Cannot reach the OfficeFix server at ${API_BASE_URL}. Check that the backend is running.`,
      0
    )
  }
  return new ApiError(error.message || 'An unexpected error occurred.', 0)
}

async function request(config) {
  try {
    const response = await http.request(config)
    return response.data
  } catch (error) {
    throw toApiError(error)
  }
}

function withoutEmpty(params) {
  return Object.fromEntries(
    Object.entries(params).filter(([, value]) => value !== undefined && value !== null && value !== '')
  )
}

// Dashboard

export function getDashboardStats() {
  return request({ method: 'GET', url: route('/dashboard/stats') })
}

// Maintenance requests

export function listRequests(filters = {}) {
  return request({ method: 'GET', url: route('/requests'), params: withoutEmpty(filters) })
}

export function getRequest(requestId) {
  return request({ method: 'GET', url: route(`/requests/${requestId}`) })
}

export function createRequest(payload) {
  return request({ method: 'POST', url: route('/requests'), data: payload })
}

export function updateRequest(requestId, changes) {
  return request({ method: 'PATCH', url: route(`/requests/${requestId}`), data: changes })
}

export function deleteRequest(requestId) {
  return request({ method: 'DELETE', url: route(`/requests/${requestId}`) })
}

// Technicians

export function listTechnicians() {
  return request({ method: 'GET', url: route('/technicians') })
}

export function createTechnician(payload) {
  return request({ method: 'POST', url: route('/technicians'), data: payload })
}

export function updateTechnician(technicianId, changes) {
  return request({ method: 'PATCH', url: route(`/technicians/${technicianId}`), data: changes })
}
