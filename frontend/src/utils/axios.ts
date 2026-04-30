import axios from 'axios';
import { authUtils } from './auth';

// Create axios instance
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 30000,
});

// Add authorization interceptor
api.interceptors.request.use(
  (config) => {
    const token = authUtils.getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle response errors (e.g., 401 unauthorized)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear auth on 401
      authUtils.clearToken();
      // Trigger re-login (component will detect auth state change)
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
