import axios from 'axios';

// Create an Axios instance with default configuration
const api = axios.create({
    // In production (Render/Unified), we use relative /api
    // In development (Vite 5173), we hit the backend directly on 5001
    baseURL: import.meta.env.PROD ? '/api' : 'http://localhost:5001/api',
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
