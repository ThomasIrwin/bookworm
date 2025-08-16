import axios from 'axios';

const api = axios.create({
    baseURL:
        import.meta.env.BOOKWORM_API_URL || 'http://localhost:8080',
    headers: {
        'Content-Type': 'application/json',
    },
});

export const apiService = {
    getUserLibrary: () => api.get('/'),
    healthCheck: () => api.get('/health'),
    // TODO
    addBookToUserLibrary: (book: any) => api.put('/book', book),
}

export default api;