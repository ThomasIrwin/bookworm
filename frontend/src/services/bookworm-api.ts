import type { AddBookRequest } from '@/interfaces/Book';
import axios from 'axios';

export const api = axios.create({
    baseURL:
        import.meta.env.BOOKWORM_API_URL || 'http://localhost:8080/api/v1',
    headers: {
        'Content-Type': 'application/json',
    },
});

export const apiService = {
    // books
    getAllBooks: () => api.get('/books/'),
    healthCheck: () => api.get('/books/health'),

    // users
    sendUserDataToServer: () => api.post('/users/me'),

    // userbooks
    getUserBooks: () => api.get("/userbooks/"),
    addBookToUserLibrary: (book: AddBookRequest) => api.put('userbooks/add-book', book),
}

export default api;