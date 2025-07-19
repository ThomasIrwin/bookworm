import React, { useEffect, useState } from 'react';
import { apiService } from './services/api';

import './App.css';

function App() {
  const [apiStatus, setApiStatus] = useState<string>('Loading...');

  useEffect(() => {
    apiService.healthCheck()
      .then(response => {
        setApiStatus(response.data);
      })
      .catch(error => {
        setApiStatus('API connection failed');
        console.error('API Error: ', error);
      });
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1> Bookworm </h1>
        <p> Backend Status: {apiStatus} </p>
      </header>
    </div>
  );
}

export default App;
