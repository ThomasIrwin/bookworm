import { Auth0Provider } from '@auth0/auth0-react'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import App from './App.tsx'
import Home from './components/home/home.tsx'
import './index.css'


const router = createBrowserRouter([
  { path: '/', element: <App /> },
  { path: '/home', element: <Home /> },
]);

createRoot(document.getElementById('root')!).render(
  <Auth0Provider
    domain='dev-ulixqg71ihyco2h1.us.auth0.com'
    clientId='dHA4AYI62HWe3i15k40QmE4LFENPiKJj'
    authorizationParams={{
      redirect_uri: 'http://localhost:3000/home',
      audience: 'http://localhost:8080/api/v1',
    }}
  >
    <StrictMode>
      <RouterProvider router={router} />
    </StrictMode>
  </Auth0Provider>
)
