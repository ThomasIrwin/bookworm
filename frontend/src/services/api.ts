import axios from 'axios';

const api = axios.create({
    baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8080',
    headers: {
        "Content-Type": 'application/json',
    },
});

export const apiService = {
    // Test server connection
    healthCheck: () => api.get('/health'),

    // User library endpoint
    getUserLibrary: () => api.get('/api/v1/library'),

    // Insert new book into user's library
    addBookToUserLibrary: (book: any) => api.put('/api/v1/book', book),
}

export default api;
