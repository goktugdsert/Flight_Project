import React from 'react';
import { X, Briefcase, ChefHat, Shield, CheckCircle, AlertTriangle, UserCheck } from 'lucide-react';
import './pages/roster.css'; 

function CrewSwitchModal({ isOpen, onClose, role, candidates, onAssign, flightRequirements, assignedIds = [] }) {
  if (!isOpen) return null;

  // --- ID CONVERSION ---
  const stringAssignedIds = assignedIds.map(id => String(id));

  const sortedCandidates = candidates.map(person => {
    let isMatch = true; 
    let messages = [];

    // License Verification
    const pLic = person.vehicleRestriction || person.vehicleRestrictions;
    const reqLic = flightRequirements.vehicleType;

    if (Array.isArray(pLic)) {
        if (!pLic.some(l => l.includes(reqLic) || reqLic.includes(l))) isMatch = false;
    } else if (pLic && reqLic) {
        if (!pLic.includes(reqLic) && !reqLic.includes(pLic)) isMatch = false;
    }

    const isAlreadyOnBoard = stringAssignedIds.includes(String(person.id));

    if (isMatch) messages.push("License Match");
    else messages.push("License Warning");

    return { ...person, isMatch, messages, isAlreadyOnBoard };
  });

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{maxWidth: '500px', display: 'flex', flexDirection: 'column', maxHeight: '90vh'}}>
        
        {/* HEADER */}
        <div className="modal-header" style={{ flexShrink: 0 }}>
          <div>
             <h3 style={{margin:0}}>Select {role === 'pilot' ? 'Pilot' : 'Cabin Crew'}</h3>
             <div style={{fontSize:'0.75rem', color:'#666', marginTop:'4px'}}>
                Required: <strong>{flightRequirements.vehicleType}</strong> 
             </div>
          </div>
          <button className="close-btn" onClick={onClose}><X size={20} /></button>
        </div>

        {/* BODY */}
        <div className="modal-body" style={{ overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
            
            <div className="candidate-list" style={{
                display: 'flex', 
                flexDirection: 'column', 
                gap: '10px',
                maxHeight: '400px',  
                overflowY: 'auto',   
                paddingRight: '5px'  
            }}>
              
              {sortedCandidates.length > 0 ? (
                  sortedCandidates.map((person) => (
                    <div key={person.id} className="info-value-box" style={{
                        justifyContent: 'space-between',
                        border: person.isAlreadyOnBoard ? '1px solid #cbd5e1' : '1px solid #e2e8f0', 
                        backgroundColor: person.isAlreadyOnBoard ? '#f1f5f9' : '#f8fafc',
                        opacity: person.isAlreadyOnBoard ? 0.6 : 1,
                        flexShrink: 0 
                    }}>
                      
                      {/* LEFT SIDE INFO */}
                      <div style={{display: 'flex', alignItems: 'center', gap: '12px'}}>
                        <div style={{position: 'relative'}}>
                          <div style={{
                              backgroundColor: role === 'pilot' ? '#e0f2fe' : '#fff7ed', 
                              padding: '12px', borderRadius: '50%', 
                              color: role === 'pilot' ? '#0369a1' : '#c2410c'
                          }}>
                            {person.type === 'Chef' || person.type === 'CHEF' ? <ChefHat size={20}/> : <Briefcase size={20} />}
                          </div>
                        </div>

                        <div>
                            <div style={{fontWeight: '700', color: '#333', display: 'flex', alignItems: 'center', gap: '5px'}}>
                               {person.name}
                               {person.isAlreadyOnBoard && 
                                 <span style={{fontSize:'0.7rem', background:'#94a3b8', color:'white', padding:'2px 6px', borderRadius:'4px', display:'flex', alignItems:'center', gap:'3px'}}>
                                   <UserCheck size={10}/> Assigned
                                 </span>
                               }
                            </div>
                            
                            <div style={{fontSize: '0.8rem', color: '#555', marginTop:'2px'}}>
                               {role === 'pilot' ? 
                                 `${person.seniority || ''} • Range: ${person.allowedRange || 0} km` : 
                                 `${person.type || ''}`
                               }
                            </div>
                            
                            {!person.isMatch && (
                                <div style={{fontSize: '0.7rem', color: '#b91c1c', marginTop:'2px', display:'flex', alignItems:'center', gap:'3px'}}>
                                    <AlertTriangle size={10}/> Wrong License ({Array.isArray(person.vehicleRestriction) ? 'B' : 'A'})
                                </div>
                            )}
                        </div>
                      </div>
                      
                      {/* ASSIGN BUTTON */}
                      <button 
                        onClick={() => onAssign(person)}
                        disabled={person.isAlreadyOnBoard} 
                        className="btn-switch" 
                        style={{
                            backgroundColor: person.isAlreadyOnBoard ? '#94a3b8' : '#0f172a',
                            color: 'white', border: 'none',
                            cursor: person.isAlreadyOnBoard ? 'not-allowed' : 'pointer',
                            padding: '8px 16px', borderRadius: '6px'
                        }}
                      >
                        {person.isAlreadyOnBoard ? 'Active' : 'Assign'}
                      </button>
                    </div>
                  ))
              ) : (
                  <div style={{padding:'20px', textAlign:'center', color:'#666'}}>
                      No available crew found.
                  </div>
              )}
            </div>
        </div>
      </div>
    </div>
  );
}

export default CrewSwitchModal;