import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API
export const authAPI = {
  register: (email, password) => api.post('/auth/register', { email, password }),
  login: (email, password) => api.post('/auth/login', { email, password }),
};

// Search API
export const searchAPI = {
  search: (query, top_k = 5) => api.post('/search/', { query, top_k }),
};

// Chat API
export const chatAPI = {
  ask: (question, top_k = 5) => api.post('/chat/', { question, top_k }),
};

// Circulars API
export const circularsAPI = {
  list: (skip = 0, limit = 20, source = null) => {
    const params = { skip, limit };
    if (source) params.source = source;
    return api.get('/circulars/', { params });
  },
  get: (id) => api.get(`/circulars/${id}`),
};

export default api;
