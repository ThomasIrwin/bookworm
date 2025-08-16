
import { useEffect, useState } from 'react'
import { apiService } from './services/bookworm-api';
import { Link } from 'react-router-dom';
import { Button } from './components/ui/button';

function App() {
  const [apiStatus, setApiStatus] = useState<string>('Loading...');

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

  return (
    <main className='landing'>
      <header className='landing-header'>
        <h1
          className=
            'flex items-center justify-center text-[70px]'
          > Boookworm </h1>
        <p
          className='flex items-center justify-center'
        >Server status: { apiStatus } </p>

          <div className='flex min-h-[100px] flex-col items-center justify-center'>
            <Link to={'/home'}>
              <Button> Go Home </Button>
            </Link>
          </div>
      </header>
    </main>
  )
}

export default App
