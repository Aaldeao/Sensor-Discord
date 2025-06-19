import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Login from './View/Login';
import Dashboard from './View/Dashboard';

function App() {
  const [view, setView] = useState(null); // null para indicar estado de carga

  useEffect(() => {
    const checkUsers = async () => {
      try {
        // Verificar si existen usuarios en la base de datos
        const response = await axios.get('http://localhost:8080/users/check');
        if (response.status === 200) {
          setView('dashboard');
        }
      } catch (error) {
        if (error.response?.status === 404) {
          console.log('No existen usuarios, redirigiendo al Login.');
          setView('login'); // No hay usuarios en el sistema
        } else {
          console.error('Error en metodo Users Check', error.message);
        }
      }
    };

    checkUsers();
  }, [view]);

  // Mientras se verifica, muestra un indicador de carga
  if (view === null) {
    return <p>Cargando...</p>;
  }

  // Renderizar la vista según el estado
  return (
    <div>
      
      {view === 'login' && <Login setView={setView} />}
      {view === 'dashboard' && <Dashboard />}
    </div>
  );
}

export default App;