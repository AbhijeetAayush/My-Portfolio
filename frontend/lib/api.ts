import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
  }
  return config
})

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear tokens and redirect to login
      if (typeof window !== 'undefined') {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        if (window.location.pathname.startsWith('/admin')) {
          window.location.href = '/admin/login'
        }
      }
    }
    return Promise.reject(error)
  }
)

export default api

// API functions
export const portfolioAPI = {
  get: () => api.get('/portfolio'),
  update: (data: any) => api.put('/portfolio', data),
}

export const blogsAPI = {
  getAll: (params?: { limit?: number; last_key?: string }) =>
    api.get('/blogs', { params }),
  getById: (id: string) => api.get(`/blogs/${id}`),
  create: (data: any) => api.post('/blogs', data),
  update: (id: string, data: any) => api.put(`/blogs/${id}`, data),
  delete: (id: string) => api.delete(`/blogs/${id}`),
}

export const commentsAPI = {
  getByBlog: (blogId: string) => api.get(`/blogs/${blogId}/comments`),
  create: (blogId: string, data: any) =>
    api.post(`/blogs/${blogId}/comments`, data),
  delete: (commentId: string) => api.delete(`/comments/${commentId}`),
}

export const likesAPI = {
  get: (blogId: string) => api.get(`/blogs/${blogId}/likes`),
  add: (blogId: string) => api.post(`/blogs/${blogId}/likes`),
}

export const authAPI = {
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),
}
