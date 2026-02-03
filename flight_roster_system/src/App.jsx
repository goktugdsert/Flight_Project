import React, { useState } from 'react';
import { Outlet, useNavigate } from 'react-router-dom'; 
import './App.css';

import {
  User,           
  LogOut,         
  Menu,           
  Home,           
  ClipboardList,  
  Save,           
  Users, 
  Plane,       
  ArrowLeft       
} from 'lucide-react';

function App() {
  // state to keep track if sidebar is open or closed
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  
  const navigate = useNavigate(); 

  // --- CHECK IF USER IS VIEWONLY ---
  const currentUser = localStorage.getItem('username');
  const isViewOnly = currentUser === 'viewonly'; 
  // -----------------------------------------------

  // logout function
  const handleLogout = () => {

    localStorage.removeItem('username');
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    navigate('/login');
  };

  return (
    <div className="app-container">
      
      {/* ===== 1. HEADER SECTION ===== */}
      <header className="app-header">
        <div className="header-right">
          <button className="header-btn user-btn">
            <User size={18} />
            <span>{currentUser || 'User'}</span>
          </button>
          <button className="header-btn exit-btn" onClick={handleLogout}>
            <LogOut size={18} />
            <span>Exit</span>
          </button>
        </div>
      </header>

      {/* ===== 2. MAIN BODY ===== */}
      <div className="app-body">
        
        {/* ===== SIDEBAR SECTION ===== */}
        <aside className={`app-sidebar ${isSidebarOpen ? 'open' : ''}`}>
          
          <div className="sidebar-top">
            
            {/* toggle menu button */}
            <button 
              className="sidebar-icon-btn toggle-btn" 
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            >
              <Menu size={24} />
            </button>
            
            {!isViewOnly && (
              <>
                {/* go to home page */}
                <button 
                  className="sidebar-icon-btn" 
                  onClick={() => navigate('/')}
                >
                  <Home size={22} />
                  <span className="sidebar-text">Home</span>
                </button>

                {/* BUTTON: PILOTS */}
                <button 
                  className="sidebar-icon-btn" 
                  onClick={() => navigate('/pilots')}
                >
                  <Plane size={22} />
                  <span className="sidebar-text">Pilots</span>
                </button>

                {/* BUTTON: CABIN CREW */}
                <button 
                  className="sidebar-icon-btn" 
                  onClick={() => navigate('/cabin-crew')}
                >
                  <Users size={22} />
                  <span className="sidebar-text">Cabin Crew</span>
                </button>
              </>
            )}
            {/* ------------------------------------------------ */}

            {/* go to saved rosters */}
            <button 
              className="sidebar-icon-btn" 
              onClick={() => navigate('/saved-rosters')}
            >
              <Save size={22} />
              <span className="sidebar-text">Saved Rosters</span>
            </button>

          </div>
          
          <div className="sidebar-bottom">
            
            {/* logout button */}
            <button 
              className="sidebar-icon-btn logout-btn"
              onClick={handleLogout}
            >
              <ArrowLeft size={22} />
              <span className="sidebar-text">Logout</span>
            </button>
          </div>
        </aside>

        {/* ===== MAIN CONTENT AREA ===== */}
        <main className="app-content">
          
          <div className="content-wrapper">
             <Outlet /> 
          </div> 
          
          {/* background clouds */}
          <img 
            src="/Cloudy 2.svg" 
            className="background-clouds" 
            alt="background clouds" 
          />

        </main>
      </div>

    </div>
  );
}

export default App;