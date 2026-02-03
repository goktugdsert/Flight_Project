import React, { useState, useEffect } from 'react';
import axios from 'axios'; 
import { MapPin, Plane, User, Languages, AlertCircle } from 'lucide-react';
import './Crew.css'; 

const PilotInfo = () => {
  // Containers to hold data (State)
  const [pilots, setPilots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Function that runs when the page opens
  useEffect(() => {
    const fetchPilots = async () => {
      try {
        // 
        const apiUrl = import.meta.env.VITE_API_URL; // Get address from .env (http://localhost:8001)
        const token = localStorage.getItem('accessToken'); 

        // Sending request to Backend
        const response = await axios.get(`${apiUrl}/api/pilots/`, {
          headers: {
            Authorization: `Bearer ${token}` 
          }
        });

        setPilots(response.data); 
        setLoading(false);

      } catch (err) {
        console.error("Error loading pilots:", err);
        setError("Could not fetch pilot data. Make sure you are logged in.");
        setLoading(false);
      }
    };

    fetchPilots();
  }, []);

  if (loading) return <div className="loading-screen">Loading Pilots...</div>;
  if (error) return <div className="error-message"><AlertCircle /> {error}</div>;

  return (
    <div className="crew-page-container">
      <h1 className="page-title">Pilot Information</h1>
      <p className="page-subtitle">Flight deck crew details and restrictions.</p>

      <div className="crew-grid">
        {pilots.map((pilot) => (
          <div key={pilot.id || pilot.pilot_id} className="crew-card">
            
            {/* Header */}
            <div className="crew-header">
              <div className="crew-title-box">
                {/* Adjusted name fields based on data coming from Backend */}
                <h3>{pilot.name || pilot.full_name || pilot.first_name}</h3>
                <span className="crew-id">P{pilot.id || pilot.pilot_id || 'N/A'}</span>
              </div>
              <span className={`status-badge ${(pilot.seniority_level || pilot.seniority || 'TRAINEE').toLowerCase()}`}>
                {pilot.seniority_level || pilot.seniority || 'TRAINEE'}
              </span>
            </div>

            {/* Body */}
            <div className="crew-body">
              <div className="info-row">
                <User size={14} className="icon-muted" />
                <span>
                  {pilot.age} Years • {pilot.gender} • {pilot.nationality}
                </span>
              </div>
              <div className="info-row">
                <Languages size={14} className="icon-muted" />
                {/* Check if Backend sends languages as a list or string */}
                <span>
                  {Array.isArray(pilot.known_languages) 
                    ? pilot.known_languages.join(', ') 
                    : pilot.known_languages || pilot.languages || 'None'}
                </span>
              </div>
            </div>

            <div className="divider"></div>

            {/* Footer */}
            <div className="crew-footer">
              <div className="tech-item">
                <span className="tech-label">Vehicle</span>
                <div className="tech-val">
                    <Plane size={14} /> 
                    {/* Backend probably returns a list, join them or use string version */}
                    {Array.isArray(pilot.vehicle_types) 
                        ? pilot.vehicle_types.join(', ') 
                        : pilot.vehicle_types || pilot.vehicleRestriction || 'Any'}
                </div>
              </div>
              <div className="tech-item">
                <span className="tech-label">Max Range</span>
                <div className="tech-val">
                    <MapPin size={14} /> 
                    {pilot.allowed_range || pilot.allowedRange || 0} km
                </div>
              </div>
            </div>

          </div>
        ))}
      </div>
    </div>
  );
};

export default PilotInfo;