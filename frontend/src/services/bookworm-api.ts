import type { Book } from '@/interfaces/Book';
import axios from 'axios';

const api = axios.create({
    baseURL:
        import.meta.env.BOOKWORM_API_URL || 'http://localhost:8080',
    headers: {
        'Content-Type': 'application/json',
    },
});

export const apiService = {
    getAllBooks: () => api.get('/books/'),
    healthCheck: () => api.get('/books/health'),

    sendUserDataToServer: (auth0Id: string, email: string) => api.post('/user/save', { auth0Id: auth0Id, email: email }),

    getUserLibrary: (auth0Id: string) => api.get("/userbooks/", {params: { user_id: auth0Id }}),

    // TODO
    addBookToUserLibrary: (book: Book) => api.put('userbooks/addbook', book),
}

export default api;