import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: { 'Content-Type': 'application/json' },
})

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

export default api
