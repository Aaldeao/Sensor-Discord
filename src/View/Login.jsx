import React, { useState } from 'react';
import axios from 'axios';
import "../styles/LoginBGamesView.css";

function Login({ setView }) { // Recibe setView como prop
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await axios.post('http://localhost:8080/users/create', {
        email,
        password,
      });
      if (response.status === 201) {
        setMessage('User created successfully.');
        setView('dashboard'); // Redirige a SteamLogin
      } else {
        setMessage('Error creating user.');
      }
    } catch (error) {
      setMessage('Server error: ' + error.response?.data?.error || error.message);
    }
  };
  return (
    <div className='loginBGames-container'>
      <h1>Login in bGames</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Email:</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Password:</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit">Send</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
}

export default Login;