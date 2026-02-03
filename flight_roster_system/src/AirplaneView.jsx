import React, { useState, useMemo } from 'react';
import { Users, Plane as PlaneIcon, User, X } from 'lucide-react';

const AirplaneView = ({ passengers = [], pilots = [], cabinCrew = [], vehicleType = "Boeing 737" }) => {
  
  // --- STATE ---
  const [tooltip, setTooltip] = useState({ 
    visible: false, x: 0, y: 0, data: null, role: '' 
  });

  // --- 1. AIRCRAFT TYPE CHECKS ---
  const vType = vehicleType ? vehicleType.toLowerCase() : "";
  const isB777 = vType.includes("777");
  const isB737 = vType.includes("737");
  // Default fallback is A320
  
  let totalCrewSlots = 6;
  if (isB777) totalCrewSlots = 10;
  else if (isB737) totalCrewSlots = 7;

  // How many crew members in the front? (Half or more)
  const frontCrewCount = Math.ceil(totalCrewSlots / 2); 
  // How many in the back?
  const backCrewCount = totalCrewSlots - frontCrewCount;

  // --- 3. AIRCRAFT CONFIGURATION ---
  const aircraftConfig = useMemo(() => {
    if (isB777) {
        return {
            name: "Boeing 777",
            businessRows: [1, 2, 3, 4, 5, 6], 
            economyRows: Array.from({ length: 35 }, (_, i) => i + 7), 
            layout: '3-3',
            aisleGap: '35px',
            seatGap: '6px'
        };
    } else {
        return {
            name: isB737 ? "Boeing 737" : "Airbus A320",
            businessRows: [1, 2, 3, 4], 
            economyRows: Array.from({ length: 29 }, (_, i) => i + 5), 
            layout: '3-3',
            aisleGap: '35px',
            seatGap: '6px'
        };
    }
  }, [vehicleType, isB777, isB737]);

  // --- DYNAMIC STYLE SETTINGS ---
  const PLANE_REAL_WIDTH = '3000px'; 
  const dynamicPlaneHeight = isB777 ? '2800px' : '2250px';
  const dynamicTopPadding = isB777 ? '680px' : '520px';
  const dynamicCockpitTop = isB777 ? '600px' : '500px'; 

  const SEAT_WIDTH = '25px';
  const SEAT_HEIGHT = '35px';

  // --- HELPER FUNCTIONS ---
  const getPassenger = (seatId) => passengers ? passengers.find(p => p.seat === seatId) : null;
  const getPilot = (index) => pilots[index];
  const getCrew = (index) => cabinCrew[index];

  // --- SEAT COMPONENT ---
  const Seat = ({ id, type = 'economy', assignedPerson, roleLabel = 'Passenger' }) => {
    const isOccupied = !!assignedPerson;
    
    let width = type === 'business' ? '35px' : SEAT_WIDTH;
    let height = SEAT_HEIGHT;
    let color = '#e0e0e0'; 
    let borderRadius = '6px';
    let textColor = '#555';
    let cursor = 'default';

    if (isOccupied) {
        cursor = 'pointer';
        if (type === 'cockpit') {
            width = '40px'; height = '50px'; borderRadius = '8px 8px 0 0';
            color = '#1e3a8a'; textColor = 'white';
        } else if (type === 'crew') {
            width = '30px'; height = '30px'; borderRadius = '50%';
            color = '#d97706'; textColor = 'white';
        } else if (type === 'business') {
            color = '#2c3e50'; textColor = 'white';
        } else {
            color = '#a92e2e'; textColor = 'white';
        }
    }

    const handleClick = (e) => {
        if (isOccupied) {
            setTooltip({
                visible: true,
                x: e.clientX,
                y: e.clientY,
                data: assignedPerson,
                role: roleLabel
            });
        }
    };

    return (
      <div
        onClick={handleClick}
        style={{
          width: width,
          height: height,
          backgroundColor: color,
          borderRadius: borderRadius,
          margin: (type === 'crew') ? '4px' : `0 ${aircraftConfig.seatGap} ${aircraftConfig.seatGap} 0`,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '10px', fontWeight: 'bold', 
          color: textColor,
          cursor: cursor,
          border: isOccupied ? `1px solid ${color}` : '1px solid #ccc',
          boxShadow: isOccupied ? '0 2px 4px rgba(0,0,0,0.2)' : 'none',
          transition: 'transform 0.1s'
        }}
        onMouseDown={(e) => e.currentTarget.style.transform = 'scale(0.95)'}
        onMouseUp={(e) => e.currentTarget.style.transform = 'scale(1)'}
      >
        {type === 'cockpit' ? 'P' : type === 'crew' ? 'C' : id}
      </div>
    );
  };

  // --- RENDER ROW ---
  const renderRow = (rowNum, type) => {
    if (type === 'business') {
        return (
            <div key={rowNum} style={{ display: 'flex', justifyContent: 'center', marginBottom: '2px' }}>
                <div style={{ display: 'flex', marginRight: aircraftConfig.aisleGap }}>
                    <Seat id={`${rowNum}A`} type={type} assignedPerson={getPassenger(`${rowNum}A`)} />
                    <Seat id={`${rowNum}C`} type={type} assignedPerson={getPassenger(`${rowNum}C`)} />
                </div>
                <div style={{ display: 'flex' }}>
                    <Seat id={`${rowNum}D`} type={type} assignedPerson={getPassenger(`${rowNum}D`)} />
                    <Seat id={`${rowNum}F`} type={type} assignedPerson={getPassenger(`${rowNum}F`)} />
                </div>
            </div>
        );
    }
    return (
        <div key={rowNum} style={{ display: 'flex', justifyContent: 'center', marginBottom: '2px' }}>
            <div style={{ display: 'flex', marginRight: aircraftConfig.aisleGap }}>
                {['A','B','C'].map(char => <Seat key={`${rowNum}${char}`} id={`${rowNum}${char}`} type={type} assignedPerson={getPassenger(`${rowNum}${char}`)} />)}
            </div>
            <div style={{ display: 'flex' }}>
                {['D','E','F'].map(char => <Seat key={`${rowNum}${char}`} id={`${rowNum}${char}`} type={type} assignedPerson={getPassenger(`${rowNum}${char}`)} />)}
            </div>
        </div>
    );
  };

  // --- DYNAMIC CREW SEAT RENDER HELPER ---
  const renderCrewSeats = (startIndex, count) => {
    return Array.from({ length: count }, (_, i) => {
        const crewIndex = startIndex + i;
        return (
            <Seat 
                key={`C${crewIndex + 1}`} 
                id={`C${crewIndex + 1}`} 
                type="crew" 
                assignedPerson={getCrew(crewIndex)} 
                roleLabel="Cabin Crew" 
            />
        );
    });
  };

  return (
    <div className="airplane-window" 
      style={{
        width: '100%', height: '650px', overflowY: 'auto', overflowX: 'hidden', 
        border: '1px solid #ddd', borderRadius: '8px', backgroundColor: '#f9f9f9', position: 'relative'
    }}>
      
      {/* --- AIRCRAFT FUSELAGE --- */}
      <div style={{
        minWidth: PLANE_REAL_WIDTH, width: PLANE_REAL_WIDTH, 
        height: dynamicPlaneHeight,
        backgroundImage: 'url("/Plane.png")', backgroundSize: '100% 100%', backgroundRepeat: 'no-repeat',
        paddingTop: dynamicTopPadding, 
        paddingBottom: '100px',
        display: 'flex', flexDirection: 'column', alignItems: 'center', 
        position: 'relative', left: '50%', transform: 'translateX(-50%)'
      }}>

        {/* 1. COCKPIT & FRONT CREW */}
        <div style={{ position: 'absolute', top: dynamicCockpitTop, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '15px' }}>
            
            {/* PILOTS (Side by Side) */}
            <div style={{ display: 'flex', gap: '30px' }}>
                <Seat id="P1" type="cockpit" assignedPerson={getPilot(0)} roleLabel="Pilot (Captain)" />
                <Seat id="P2" type="cockpit" assignedPerson={getPilot(1)} roleLabel="Pilot (First Officer)" />
            </div>
            
            {/* FRONT CABIN CREW (DYNAMIC) */}
            <div style={{ 
                display: 'flex', 
                gap: '10px', 
                justifyContent: 'center', 
                flexWrap: 'wrap', 
                maxWidth: '200px' 
            }}>
                {renderCrewSeats(0, frontCrewCount)}
            </div>
        </div>

        {/* 2. BUSINESS CLASS SECTION */}
        <div className="business-section" style={{ marginBottom: '30px', marginTop: '100px' }}>
          <h4 style={{ textAlign: 'center', fontSize: '12px', color: '#666', letterSpacing:'2px', margin: '0 0 10px 0' }}>
            BUSINESS
          </h4>
          {aircraftConfig.businessRows.map(row => renderRow(row, 'business'))}
        </div>

        {/* 3. ECONOMY CLASS SECTION */}
        <div className="economy-section">
          <h4 style={{ textAlign: 'center', fontSize: '12px', color: '#666', letterSpacing:'2px', margin: '0 0 10px 0' }}>
            ECONOMY
          </h4>
          {aircraftConfig.economyRows.map(row => renderRow(row, 'economy'))}
        </div>

        {/* 4. REAR CABIN CREW (DYNAMIC) */}
        <div style={{ 
            marginTop: '20px', 
            display: 'flex', 
            gap: '4px', 
            justifyContent: 'center',
            flexWrap: 'wrap',
            maxWidth: '180px'
        }}>
            {renderCrewSeats(frontCrewCount, backCrewCount)}
        </div>

      </div>

      {/* --- TOOLTIP --- */}
      {tooltip.visible && tooltip.data && (
        <div style={{
          position: 'fixed', 
          top: tooltip.y + 10,
          left: tooltip.x + 10,
          backgroundColor: 'rgba(255, 255, 255, 0.98)', 
          padding: '15px', 
          borderRadius: '8px',
          boxShadow: '0 10px 40px rgba(0,0,0,0.4)', 
          zIndex: 10000, 
          minWidth: '220px',
          border: '1px solid #ccc'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px', paddingBottom: '8px', borderBottom: '1px solid #eee' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                {tooltip.role.includes('Pilot') ? <PlaneIcon size={18} color="#1e3a8a"/> : 
                 tooltip.role.includes('Crew') ? <Users size={18} color="#d97706"/> : 
                 <User size={18} color="#a92e2e"/>}
                <span style={{ fontWeight: 'bold', fontSize: '1rem', color: '#333' }}>{tooltip.role}</span>
            </div>
            <button onClick={() => setTooltip({ visible: false, x: 0, y: 0, data: null, role: '' })} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#999' }}>
                <X size={18} />
            </button>
          </div>
          <div style={{ fontSize: '0.9rem', color: '#444', lineHeight: '1.6' }}>
            <div><strong style={{color:'#666'}}>Name:</strong> {tooltip.data.name}</div>
            {tooltip.data.id && (
                <div>
                    <strong style={{color:'#666'}}>ID:</strong>{' '}

                    {tooltip.role.toLowerCase().includes('pilot') ? 'P' : 
                    tooltip.role.toLowerCase().includes('crew') ? 'C' : ''}
                    {tooltip.data.id}
                </div>
      )}
            {tooltip.data.seat && <div><strong style={{color:'#666'}}>Seat:</strong> {tooltip.data.seat}</div>}
          </div>
        </div>
      )}

    </div>
  );
};

export default AirplaneView;