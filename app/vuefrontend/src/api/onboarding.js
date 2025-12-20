import axios from 'axios'

/**
 * Onboarding API Service
 * Handles tenant workspace creation during onboarding flow
 */

/**
 * Get API base URL based on environment
 */
const getApiUrl = () => {
  const isLocalDev = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  
  if (isLocalDev) {
    // Backend supports both endpoints: /api/onboarding/ and /api/onboarding/create-tenant/
    return '/api/onboarding/'
  } else {
    const baseUrl = window.__API_BASE_URL || 'http://localhost:8000'
    const cleanBase = baseUrl.replace(/\/+$/, '')
    return `${cleanBase}/api/onboarding/`
  }
}

/**
 * Create tenant workspace
 * @param {Object} data - Onboarding data
 * @param {string} data.business_name - Business name
 * @param {string} data.business_type - Business type
 * @param {File} data.logo - Company logo file (optional)
 * @param {Object} data.admin - Admin user data
 * @param {string} data.admin.name - Admin full name
 * @param {string} data.admin.email - Admin email
 * @param {string} data.admin.password - Admin password
 * @param {string} data.address - Business address (optional)
 * @param {Array<string>} data.preferences - Selected module preferences
 * @returns {Promise} API response
 */
export const createTenantWorkspace = async (data) => {
  const formData = new FormData()
  
  // Backend expects: company_name, email, client_type, logo, address, admin[name], admin[password], preferences
  
  // Append business information (backend field names)
  formData.append('company_name', data.business_name || data.company_name)
  formData.append('client_type', data.business_type || data.client_type)
  
  // Append admin email (backend uses this to create the admin user)
  formData.append('email', data.admin?.email || data.email)
  
  // Append logo if provided
  if (data.logo) {
    formData.append('logo', data.logo)
  }
  
  // Append address if provided
  if (data.address) {
    formData.append('address', data.address)
  }
  
  // Append strategic fields if provided
  if (data.monthly_operations) {
    formData.append('monthly_operations', data.monthly_operations)
  }
  
  if (data.crew_count) {
    formData.append('crew_count', data.crew_count.toString())
  }
  
  if (data.recommended_plan) {
    formData.append('recommended_plan', data.recommended_plan)
  }
  
  // Append admin name and password if provided
  // Backend supports both nested (admin[name], admin[password]) and flat (admin_name, admin_password) formats
  if (data.admin?.name) {
    formData.append('admin[name]', data.admin.name)
    formData.append('admin_name', data.admin.name) // Flat format for compatibility
  }
  
  if (data.admin?.password) {
    formData.append('admin[password]', data.admin.password)
    formData.append('admin_password', data.admin.password) // Flat format for compatibility
  }
  
  // Append preferences array
  // Enviar cada preferencia como un campo separado para compatibilidad con FormData
  if (data.preferences && Array.isArray(data.preferences) && data.preferences.length > 0) {
    data.preferences.forEach((pref) => {
      formData.append('preferences', pref)
    })
  }
  
  try {
    const apiUrl = getApiUrl()
    
    // Log payload for debugging (don't log password in production)
    console.log('Onboarding API Request:', {
      url: apiUrl,
      company_name: formData.get('company_name'),
      email: formData.get('email'),
      client_type: formData.get('client_type'),
      has_logo: !!formData.get('logo')
    })
    
    const response = await axios.post(apiUrl, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 300000 // 5 minutes timeout for tenant creation
    })
    
    console.log('Onboarding API Response:', response.data)
    return response.data
  } catch (error) {
    console.error('Onboarding API Error:', error)
    
    // Re-throw with enhanced error information
    if (error.response) {
      // Server responded with error status
      const errorMessage = error.response.data?.error || 
                          error.response.data?.detail || 
                          error.response.data?.message ||
                          `Server error: ${error.response.status} ${error.response.statusText}`
      
      console.error('Server Error Response:', {
        status: error.response.status,
        data: error.response.data
      })
      
      throw {
        message: errorMessage,
        status: error.response.status,
        data: error.response.data
      }
    } else if (error.request) {
      // Request was made but no response received
      console.error('Network Error - No response received:', {
        url: getApiUrl(),
        message: error.message
      })
      
      // Verificar si es un error de proxy
      const isProxyError = error.message && (
        error.message.includes('Proxy error') || 
        error.message.includes('ECONNREFUSED') ||
        error.code === 'ECONNREFUSED'
      )
      
      const errorMessage = isProxyError
        ? 'Could not connect to backend. Please verify:\n1. Backend is running (docker compose up backend)\n2. Port 8000 is accessible\n3. Vue development server has been restarted'
        : 'Could not connect to server. Please verify that the backend is running at http://localhost:8000'
      
      throw {
        message: errorMessage,
        status: 0,
        data: null,
        isProxyError
      }
    } else {
      // Error setting up the request
      console.error('Request Setup Error:', error.message)
      
      throw {
        message: error.message || 'Unknown error creating workspace',
        status: 0,
        data: null
      }
    }
  }
}

/**
 * Validate business name availability (future enhancement)
 * @param {string} businessName - Business name to validate
 * @returns {Promise} API response
 */
export const validateBusinessName = async (businessName) => {
  // TODO: Implement when backend endpoint is available
  // This can be used for real-time validation during Step 1
  return Promise.resolve({ available: true })
}

