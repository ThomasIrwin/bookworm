
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth0 } from '@auth0/auth0-react';
import { apiService } from './services/bookworm-api';
import  LoginButton  from '@/components/landing-components/login-button';

function App() {
  const [apiStatus, setApiStatus] = useState<string>('Loading...');
  const { isAuthenticated, isLoading } = useAuth0();
  const navigate = useNavigate();

  useEffect( () => {
    apiService.healthCheck()
      .then( response => {
        setApiStatus(
          prevApistatus => prevApistatus = response.data
        );
      })
      .catch( error => {
        setApiStatus(
          prevApistatus => prevApistatus = "Connection Failed"
        );
        console.error('API Error: ', error)
      })
  }, []);

  useEffect( () => {
    if (isAuthenticated && !isLoading) {
      navigate('/home');
    }
  }, [isAuthenticated, isLoading, navigate])

  return (
    <main className='flex justify-center'>
      <header>
        <h1 className='text-[70px]'> Boookworm </h1>
        <p className='flex justify-center mb-5'>Server status: { apiStatus } </p>
        <div className='flex justify-center'>
          <LoginButton />
        </div>
      </header>
    </main>
  )
}

export default App;
