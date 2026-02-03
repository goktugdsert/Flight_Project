// src/AppRouter.jsx
import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

import App from './App';

import Login from './pages/login';
import Home from './pages/home';
import Roster from './pages/roster';
import SavedRosters from './pages/SavedRosters'
import PilotInfo from './pages/PilotInfo';
import CabinCrewInfo from './pages/CabinCrew';

function AppRouter() {
  const HomeCheck = () => {
    const user = localStorage.getItem('username');
    if (user === 'viewonly') {
        return <Navigate to="/saved-rosters" replace />;
    }
    return <Home />;
  };
  return (
    <Routes>
      
      {/* 1. LOGIN PAGE */}
      <Route path="/login" element={<Login />} />

      {/* 2. OTHER PAGES */}
      <Route path="/" element={<App />}>
        
        <Route index element={<HomeCheck />} /> 
        
        <Route path="home" element={<HomeCheck />} />

        <Route path="roster" element={<Roster />} />
        <Route path="saved-rosters" element={<SavedRosters />} />
        <Route path="pilots" element={<PilotInfo />} />
        <Route path="cabin-crew" element={<CabinCrewInfo />} />
      
      </Route>

    </Routes>
  );
}

export default AppRouter;