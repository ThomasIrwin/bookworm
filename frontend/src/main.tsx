import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import Home from './components/home-component/home.tsx'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import { Auth0Provider } from '@auth0/auth0-react';


const router = createBrowserRouter([
  { path: '/', element: <App /> },
  { path: '/home', element: <Home />},
]);

createRoot(document.getElementById('root')!).render(
  <Auth0Provider
    domain='dev-ulixqg71ihyco2h1.us.auth0.com'
    clientId='dHA4AYI62HWe3i15k40QmE4LFENPiKJj'
    authorizationParams={{
      redirect_uri: 'http://localhost:3000/home',
      // audience: '', Implement aftersetting up client auth
      // scope: ''
    }}
  >
    <StrictMode>
      <RouterProvider router={ router } />
    </StrictMode>
  </Auth0Provider>
)
