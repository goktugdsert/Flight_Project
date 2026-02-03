import React, { useState } from 'react';
import axios from 'axios';
import { Users, Plane, Info, MapPin, X, Armchair } from 'lucide-react';
import './pages/roster.css';

function PassengerModal({ passenger, onClose, onUpdate }) {
  const [loading, setLoading] = useState(false);

  if (!passenger) return null;

  // --- SEAT ASSIGNMENT FUNCTION ---
  const handleAssignSeat = async () => {
    setLoading(true);
    try {
      const apiUrl = import.meta.env.VITE_API_URL;
      const token = localStorage.getItem('accessToken');

      await axios.post(
        `${apiUrl}/api/roster/assign-seat/`,
        { 
          passenger_id: passenger.id,
          flight_number: passenger.flightId 
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      alert(`Success! Seat assigned.`);
      if (onUpdate) onUpdate(); // refresh the main page
      onClose(); 

    } catch (error) {
      console.error("Assign Error:", error);
      alert("Failed to assign seat. Try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        
        <div className="modal-header">
          <h3>Passenger Details</h3>
          <button className="close-btn" onClick={onClose}><X size={20} /></button>
        </div>

        <div className="modal-body">
          <div className="info-grid">
            
            <div className="info-group">
              <label>Passenger ID</label>
              <div className="info-value-box"><Users size={14} /> {passenger.id}</div>
            </div>

            <div className="info-group">
              <label>Flight ID</label>
              <div className="info-value-box"><Plane size={14} /> {passenger.flightId}</div>
            </div>

            <div className="info-group full-width">
              <label>Passenger Info</label>
              <div className="info-value-box" style={{justifyContent: 'space-between'}}>
                <span><strong>{passenger.name}</strong></span>
                <span style={{fontSize: '0.85rem', color: '#666'}}>
                  {passenger.gender}, {passenger.age} y/o ({passenger.nationality})
                </span>
              </div>
            </div>

             <div className="info-group">
              <label>Seat Type</label>
              <div className="info-value-box">{passenger.seatType}</div>
            </div>

            {/* --- SEAT STATUS AND BUTTON --- */}
            <div className="info-group full-width">
              <label>Seat Assignment Status</label>
              
              {passenger.age <= 2 ? (
                <div className="no-seat-warning">
                  <strong><Info size={14}/> Infant Passenger</strong>
                  <span className="sub-detail">Linked Parent ID: <strong>{passenger.parentId}</strong></span>
                </div>
              ) : (
                <>
                  {passenger.seat ? (
                    <div className="seat-display">
                      <MapPin size={14}/> Designated Seat: <strong>{passenger.seat}</strong>
                    </div>
                  ) : (
                    <div className="pending-seat-box">
                      <div className="no-seat-warning" style={{marginBottom: '10px'}}>
                        <strong>Pending Assignment</strong>
                      </div>
                      
                      <button 
                        onClick={handleAssignSeat} 
                        disabled={loading}
                        className="assign-btn"
                        style={{
                            width: '100%', padding: '10px', background: '#0f172a', color: 'white',
                            border: 'none', borderRadius: '6px', cursor: 'pointer', display: 'flex',
                            justifyContent: 'center', alignItems: 'center', gap: '8px'
                        }}
                      >
                        <Armchair size={16} /> 
                        {loading ? 'Assigning...' : 'Assign Automatic Seat'}
                      </button>
                    </div>
                  )}
                </>
              )}
            </div>

            {/* --- AFFILIATED PASSENGERS --- */}
            <div className="info-group full-width">
                <label>Affiliated Passengers</label>
                <div className="info-value-box" style={{background: '#f8fafc'}}>
                    {passenger.affiliatedIds && passenger.affiliatedIds.length > 0 
                        ? passenger.affiliatedIds.join(", ") 
                        : <span style={{color: '#999'}}>None</span>}
                </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
}

export default PassengerModal;