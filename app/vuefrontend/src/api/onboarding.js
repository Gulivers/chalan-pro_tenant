import axios from 'axios'

/**
 * Onboarding API Service
 * Handles tenant workspace creation during onboarding flow
 */

const getApiBase = () => {
  const isLocalDev = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  if (isLocalDev) {
    return ''
  }
  const baseUrl = window.__API_BASE_URL || 'http://localhost:8000'
  return baseUrl.replace(/\/+$/, '')
}

const getApiUrl = () => `${getApiBase()}/api/onboarding/`
const getVerifyApiUrl = () => `${getApiBase()}/api/onboarding/verify/`
const getConfigApiUrl = () => `${getApiBase()}/api/onboarding/config/`

export const fetchOnboardingConfig = async () => {
  const response = await axios.get(getConfigApiUrl())
  return response.data
}

/**
 * Create tenant workspace
 */
export const createTenantWorkspace = async (data, turnstileToken = '') => {
  const formData = new FormData()

  formData.append('company_name', data.business_name || data.company_name)
  formData.append('client_type', data.business_type || data.client_type)
  formData.append('email', data.admin?.email || data.email)

  if (turnstileToken) {
    formData.append('turnstile_token', turnstileToken)
    formData.append('cf_turnstile_response', turnstileToken)
  }

  if (data.logo) {
    formData.append('logo', data.logo)
  }
  if (data.address) {
    formData.append('address', data.address)
  }
  if (data.monthly_operations) {
    formData.append('monthly_operations', data.monthly_operations)
  }
  if (data.crew_count) {
    formData.append('crew_count', data.crew_count.toString())
  }
  if (data.recommended_plan) {
    formData.append('recommended_plan', data.recommended_plan)
  }
  if (data.landing_selected_plan) {
    formData.append('landing_selected_plan', data.landing_selected_plan)
  }
  if (data.admin?.name) {
    formData.append('admin[name]', data.admin.name)
    formData.append('admin_name', data.admin.name)
  }
  if (data.admin?.password) {
    formData.append('admin[password]', data.admin.password)
    formData.append('admin_password', data.admin.password)
  }
  if (data.preferences && Array.isArray(data.preferences) && data.preferences.length > 0) {
    data.preferences.forEach((pref) => {
      formData.append('preferences', pref)
    })
  }

  try {
    const apiUrl = getApiUrl()
    const response = await axios.post(apiUrl, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 120000,
    })
    return response.data
  } catch (error) {
    if (error.response) {
      const errorMessage = error.response.data?.error ||
        error.response.data?.detail ||
        error.response.data?.message ||
        `Server error: ${error.response.status} ${error.response.statusText}`
      throw {
        message: errorMessage,
        status: error.response.status,
        data: error.response.data,
      }
    }
    if (error.request) {
      throw {
        message: 'Could not connect to server. Please verify that the backend is running.',
        status: 0,
        data: null,
      }
    }
    throw {
      message: error.message || 'Unknown error creating workspace',
      status: 0,
      data: null,
    }
  }
}

export const verifyOnboardingEmail = async (token) => {
  try {
    const response = await axios.post(
      getVerifyApiUrl(),
      { token },
      { timeout: 300000 },
    )
    return response.data
  } catch (error) {
    if (error.response) {
      throw {
        message: error.response.data?.error || 'Verification failed.',
        status: error.response.status,
        data: error.response.data,
      }
    }
    throw {
      message: 'Could not connect to server.',
      status: 0,
      data: null,
    }
  }
}

export const validateBusinessName = async () => Promise.resolve({ available: true })
