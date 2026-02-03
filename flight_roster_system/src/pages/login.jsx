import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom'; 
import axios from 'axios'; 
import './login.css';

import cloudImage from '/cloud.png'; 
import planeImage from '/plane-circle.png'; 

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  
  const [error, setError] = useState(''); 
  
  const navigate = useNavigate();

  // --- UPDATED LOGIN FUNCTION ---
  const handleLogin = async (e) => {
    e.preventDefault();
    setError(''); 

    // getting the address from .env file (http://localhost:8001)
    const apiUrl = import.meta.env.VITE_API_URL;

    try {
      console.log("Sending request to Backend...", apiUrl);

      // 2. REAL REQUEST TO BACKEND (POST)
      const response = await axios.post(`${apiUrl}/api/token/`, {
        username: username,
        password: password
      });

      // 3. IF SUCCESSFUL, GET THE TOKEN
      const accessToken = response.data.access;
      const refreshToken = response.data.refresh;

      // 4. SAVE TOKEN TO BROWSER 
      localStorage.setItem('accessToken', response.data.access);
      localStorage.setItem('refreshToken', response.data.refresh);
      localStorage.setItem('username', username);

      console.log("Login Successful! Token received.");
      
      // 5. REDIRECT TO HOME PAGE
      navigate('/'); 

    } catch (err) {
      // THIS RUNS IF THERE IS AN ERROR
      console.error("Login Hatası:", err);
      
      if (!apiUrl) {
        setError("API address not found (check .env file!)");
      } else if (err.response && err.response.status === 401) {
        setError("Username or password incorrect!");
      } else {
        setError("Cannot connect to server. Is Backend running?");
      }
    }
  };

  return (
    <div className="login-container">
      
      {/* LEFT SIDE FORM AREA */}
      <div className="login-left">
        
        {/* --- ANIMATED CLOUDS --- */}
        <div className="clouds-container">
          <img src={cloudImage} className="cloud-item c1" alt="cloud" />
          <img src={cloudImage} className="cloud-item c2" alt="cloud" />
          <img src={cloudImage} className="cloud-item c3" alt="cloud" />
          <img src={cloudImage} className="cloud-item c4" alt="cloud" />
          <img src={cloudImage} className="cloud-item c5" alt="cloud" />
        </div>

        {/* Form Box */}
        <div className="login-form-wrapper">
          
          <div className="welcome-container">
            <h2 className="welcome-title">
              Welcome to Bilgi Flight Roster System!
            </h2>
            <p className="welcome-subtitle">
              Please sign in to manage your flights.
            </p>
          </div>
          
          <form onSubmit={handleLogin} className="input-group">
            
            {/* --- ERROR MESSAGE AREA --- */}
            {error && (
              <div style={{ color: 'red', marginBottom: '10px', fontSize: '14px', fontWeight: 'bold' }}>
                {error}
              </div>
            )}

            <div className="input-group">
              <label htmlFor="username">Username:</label> 
              <input 
                id="username"    
                type="text" 
                className="styled-input"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required 
              />
            </div>

            <div className="input-group" style={{ marginTop: '15px' }}>
              <label htmlFor="password">Password:</label> 
              <input 
                id="password"   
                type="password" 
                className="styled-input"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>

            <button type="submit" className="login-btn">
              Login
            </button>
          </form>
        </div>

      </div>

      {/* RIGHT SIDE IMAGE AREA */}
      <div className="login-right">
        <img src={planeImage} alt="Airplane Illustration" className="plane-illustration" />
      </div>

    </div>
  );
};

export default Login;