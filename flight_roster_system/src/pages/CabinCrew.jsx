import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Utensils, Languages, User, Plane, AlertCircle, Loader } from 'lucide-react';
import './Crew.css';

const CabinCrewInfo = () => {
  const [attendants, setAttendants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCrew = async () => {
      try {
        // 
        const apiUrl = import.meta.env.VITE_API_URL;
        const token = localStorage.getItem('accessToken');

        const response = await axios.get(`${apiUrl}/api/attendants/`, {
          headers: { Authorization: `Bearer ${token}` }
        });

        console.log("Cabin Crew Data:", response.data);
        setAttendants(response.data);
        setLoading(false);

      } catch (err) {
        console.error("Error loading crew:", err);
        setError("Could not fetch cabin crew data.");
        setLoading(false);
      }
    };

    fetchCrew();
  }, []);

  if (loading) return <div className="loading-screen"><Loader className="spin"/> Loading Cabin Crew...</div>;
  if (error) return <div className="error-message"><AlertCircle /> {error}</div>;

  return (
    <div className="crew-page-container">
      <h1 className="page-title">Cabin Crew Information</h1>
      <p className="page-subtitle">Attendants, Chiefs and Chefs management.</p>

      <div className="crew-grid">
        {attendants.map((attendant) => (
          // Using attendant_id as the unique key
          <div key={attendant.attendant_id || attendant.id} className="crew-card">
            
            <div className="crew-header">
              <div className="crew-title-box">
                {/* Backend sends 'full_name', prioritizing that */}
                <h3>{attendant.full_name || attendant.name || "Unknown Name"}</h3>
                <span className="crew-id">C{attendant.attendant_id || attendant.id}</span>
              </div>
              
              <span className={`status-badge type-${(attendant.attendant_type || 'Regular').toLowerCase()}`}>
                {attendant.attendant_type}
              </span>
            </div>

            <div className="crew-body">
              <div className="info-row">
                <User size={14} className="icon-muted" />
                <span>
                  {attendant.age} Years • {attendant.gender} • {attendant.nationality}
                </span>
              </div>
              <div className="info-row">
                <Languages size={14} className="icon-muted" />
                <span>
                  {/* Languages come as a list, joining them with commas */}
                  {Array.isArray(attendant.known_languages) 
                    ? attendant.known_languages.join(', ') 
                    : attendant.known_languages || 'None'}
                </span>
              </div>
              
              {/* Show recipes only if the attendant is a CHEF */}
              {attendant.attendant_type === 'CHEF' && (
                <div className="chef-recipes-box">
                  <span className="recipe-title"><Utensils size={12}/> Signature Recipes:</span>
                  <p>
                    {/* Recipes come as 'known_recipes' */}
                    {attendant.known_recipes && attendant.known_recipes.length > 0
                      ? attendant.known_recipes.join(', ') 
                      : "No recipes listed"}
                  </p>
                </div>
              )}
            </div>

            <div className="divider"></div>

            <div className="crew-footer">
              <div className="tech-item full-width">
                <span className="tech-label">Vehicle Permissions</span>
                <div className="tech-val">
                  <Plane size={14} /> 
                  {/* Vehicle permissions come as 'vehicle_types' */}
                  {Array.isArray(attendant.vehicle_types) 
                    ? attendant.vehicle_types.join(', ') 
                    : "Any"}
                </div>
              </div>
            </div>

          </div>
        ))}
      </div>
    </div>
  );
};

export default CabinCrewInfo;