
import LoginButton from '@/components/landing-components/login-button';
import { useAuth0 } from '@auth0/auth0-react';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAxiosInterceptor } from './hooks/use-axios-interceptor';
import { apiService } from './services/bookworm-api';

function App() {
  useAxiosInterceptor();

  const [apiStatus, setApiStatus] = useState<string>('Loading...');
  const { isAuthenticated, isLoading } = useAuth0();
  const navigate = useNavigate();

  useEffect(() => {
    apiService.healthCheck()
      .then(response => setApiStatus(response.data))
      .catch(error => {
        setApiStatus("Connection Failed");
        console.error('API Error: ', error)
      })
  }, []);

  useEffect(() => {
    if (isAuthenticated && !isLoading) {
      navigate('/home');
    }
  }, [isAuthenticated, isLoading, navigate])

  return (
    <main className='dark flex justify-center'>
      <header>
        <h1 className='text-[70px]'> Boookworm </h1>
        <p className='flex justify-center mb-5'>Server status: {apiStatus} </p>
        <div className='flex justify-center'>
          <LoginButton />
        </div>
      </header>
    </main>
  )
}

export default App;
