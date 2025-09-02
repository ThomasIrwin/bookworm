import axios from 'axios';
import { useAuth0 } from '@auth0/auth0-react';


async function getAccessToken() {
    const { getAccessTokenSilently } = useAuth0();
    const token = await getAccessTokenSilently();

    return token;
}

const api = axios.create({
    baseURL:
        import.meta.env.BOOKWORM_API_URL || 'http://localhost:8080',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getAccessToken()}`
    },
});

export const apiService = {
    getUserLibrary: () => api.get('/'),
    healthCheck: () => api.get('/health'),
    // TODO
    addBookToUserLibrary: (book: any) => api.put('/book', book),
}

export default api;