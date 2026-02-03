import React, { useState } from 'react';
import { Users, Search, Link } from 'lucide-react'; 
import './pages/roster.css';

function PassengerPanel({ passengers, onPassengerClick }) {
  const [searchTerm, setSearchTerm] = useState('');

  // Filtering logic
  const filteredPassengers = passengers.filter(p => 
    p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    p.id.includes(searchTerm) ||
    (p.seat && p.seat.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const findPassengerName = (id) => {
    const found = passengers.find(p => String(p.id) === String(id));
    return found ? `${found.name} (${found.seat || 'No Seat'})` : `Unknown ID: ${id}`;
  };

  // --- ICON CLICK EVENT ---
  const handleLinkClick = (e, passenger) => {
    e.stopPropagation(); 

    let message = `🔗 Connections for ${passenger.name}:\n\n`;
    let hasConnection = false;

    // 1. If this person has a parent/guardian (Parent ID)
    if (passenger.parentId) {
        message += `• Parent/Guardian: ${findPassengerName(passenger.parentId)}\n`;
        hasConnection = true;
    }

    // 2. If there are others affiliated with this person (Affiliated IDs)
    if (passenger.affiliatedIds && passenger.affiliatedIds.length > 0) {
        passenger.affiliatedIds.forEach(id => {
            message += `• Traveling with: ${findPassengerName(id)}\n`;
        });
        hasConnection = true;
    }

    if (hasConnection) {
        alert(message);
    }
  };

  return (
    <div className="panel-container passenger-panel">
      <div className="panel-header-search">
         <h3 className="panel-title">Passengers</h3>
         <div className="search-bar-container">
            <Search size={16} className="search-icon" />
            <input 
              type="text" 
              placeholder="Search..." 
              className="search-input" 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
         </div>
      </div>
      <div className="table-wrapper">
        <table className="passenger-table">
          <thead>
            <tr><th>Name</th><th>ID</th><th>Seat</th></tr>
          </thead>
          <tbody>
            {filteredPassengers.length > 0 ? (
              filteredPassengers.map((p, index) => {
                
                // Connection Check
                const isConnected = (p.affiliatedIds && p.affiliatedIds.length > 0) || p.parentId;

                return (
                  <tr 
                     key={index} 
                     onClick={() => onPassengerClick(p)} 
                     className="clickable-row"
                  >
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        {p.name}
                        
                        {/* ICON AND CLICK EVENT */}
                        {isConnected && (
                          <span 
                            onClick={(e) => handleLinkClick(e, p)}
                            style={{ cursor: 'pointer', padding: '2px' }} 
                            title="Click to see connections"
                          >
                            <Link size={15} color="#2563eb" />
                          </span>
                        )}
                      </div>
                    </td>
                    <td>{p.id}</td>
                    <td>
                      {p.seat ? (
                        <span className="seat-badge">{p.seat}</span>
                      ) : (
                        <span className="no-seat-badge">
                          {p.age <= 2 ? "Infant" : "Not Assigned"}
                        </span>
                      )}
                    </td>
                  </tr>
                );
              })
            ) : (
              <tr>
                <td colSpan="3" style={{ textAlign: "center", padding: "20px", color: "#999" }}>
                  No passengers found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default PassengerPanel;