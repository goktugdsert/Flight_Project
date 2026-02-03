import React from 'react';
import { Users, ArrowRight } from 'lucide-react';
import './pages/roster.css'; 

function CrewPanel({ pilots, cabinCrew, onSwitchClick, onSaveClick }) {
  return (
    <div className="panel-container crew-panel">
      <div className="panel-header">
        <h3 className="panel-title"><Users size={18} /> Crew Management</h3>
      </div>
      
      <div className="action-buttons">
        
        <button className="btn btn-assign" onClick={onSaveClick}>
            Save Roster
        </button>
      </div>
      
      {/* Pilots Section */}
      <div className="table-section">
        <div className="table-header">Pilots</div>
        <div className="table-body">
          {pilots.map((pilot, index) => (
            <div key={index} className="table-row">
              <span className="person-name">{pilot.name}
                <span style={{ fontSize: '0.85em', color: '#666', marginLeft: '6px' }}>
                   ({pilot.role})
                </span>
              </span>
              
              <button 
                className="btn-switch" 
                onClick={() => onSwitchClick('pilot', index)}
              >
                Switch <ArrowRight size={12} style={{marginLeft: 5}}/>
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Cabin Crew Section */}
      <div className="table-section">
        <div className="table-header">Cabin Crew</div>
        <div className="table-body">
          {cabinCrew.map((crew, index) => (
            <div key={index} className="table-row">
              <span className="person-name">{crew.name}
                <span style={{ fontSize: '0.85em', color: '#666', marginLeft: '6px' }}>
                   ({crew.role})
                </span>
              </span>
              <button 
                className="btn-switch" 
                onClick={() => onSwitchClick('cabin', index)}
              >
                Switch <ArrowRight size={12} style={{marginLeft: 5}}/>
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default CrewPanel;