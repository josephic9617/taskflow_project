import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: { 'Content-Type': 'application/json' },
})

// --- Interceptors ---
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // Clear token and trigger custom event for App.vue to pick up
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      window.dispatchEvent(new CustomEvent('auth-unauthorized'))
    }
    return Promise.reject(error)
  }
)

export const authApi = {
  login: (username, password) => api.post('/token/', { username, password }),
  refresh: (refresh) => api.post('/token/refresh/', { refresh }),
}

export const boardsApi = {
  list: () => api.get('/boards/'),
  get: (id) => api.get(`/boards/${id}/`),
  create: (data) => api.post('/boards/', data),
  update: (id, data) => api.patch(`/boards/${id}/`, data),
  delete: (id) => api.delete(`/boards/${id}/`),
  seed: (id) => api.post(`/boards/${id}/seed/`),
}

export const columnsApi = {
  create: (data) => api.post('/columns/', data),
  update: (id, data) => api.patch(`/columns/${id}/`, data),
  delete: (id) => api.delete(`/columns/${id}/`),
}

export const tasksApi = {
  create: (data) => api.post('/tasks/', data),
  update: (id, data) => api.patch(`/tasks/${id}/`, data),
  delete: (id) => api.delete(`/tasks/${id}/`),
  move: (data) => api.post('/tasks/move/', data),
}

export function getErrorMessage(error, fallback = 'Something went wrong') {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail
    const firstError = Object.values(error.response?.data || {})
      .flat()
      .find(Boolean)

    if (typeof detail === 'string') return detail
    if (typeof firstError === 'string') return firstError
    if (error.message) return error.message
  }

  return error instanceof Error ? error.message : fallback
}

export default api
