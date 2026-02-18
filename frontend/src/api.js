import axios from 'axios';

// Create an Axios instance with default configuration
const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5001',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add a request interceptor (e.g., to attach API key if we store it globally)
api.interceptors.request.use((config) => {
    // For now, API key is passed per request header manually in components
    // But we could automate it here if we context/store
    return config;
}, (error) => {
    return Promise.reject(error);
});

export default api;
