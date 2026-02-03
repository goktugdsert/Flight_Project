import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom'; 
import axios from 'axios'; 
import AirplaneView from "../AirplaneView"; 
import CrewPanel from "../CrewPanel";          
import PassengerPanel from "../PassengerPanel"; 
import PassengerModal from "../PassengerModal"; 
import CrewSwitchModal from "../CrewSwitchModal";
import '../pages/roster.css'; 
import { 
  Plane, Calendar, Clock, Utensils, Loader, ArrowLeft, MapPin, Info
} from 'lucide-react';

function Roster() {
  const location = useLocation(); 
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(false);
  const [selectedPassenger, setSelectedPassenger] = useState(null);

  const [pilots, setPilots] = useState([]);
  const [cabinCrew, setCabinCrew] = useState([]);
  const [passengers, setPassengers] = useState([]);

  // Candidate List for Switch Modal
  const [availableCandidates, setAvailableCandidates] = useState([]);

  const [flightDetails, setFlightDetails] = useState({
    flightNo: "---", 
    date: "---",
    time: "---",
    duration: "---",
    distance: "0",
    source: { country: "", city: "Departure", airport: "-", code: "DEP" },
    destination: { country: "", city: "Arrival", airport: "-", code: "ARR" },
    vehicle: { type: "Unknown", seats: 0, menu: "Standard" },
    shared: { isShared: false, airline: "", flightNumber: "" }
  });

  // --- 1. FETCH ROSTER DATA (DUPLICATE PROTECTION) ---
  const fetchRosterData = async (flightIdToFetch, manualPilots = null, manualAttendants = null) => {
    if (!flightIdToFetch) return;

    setLoading(true);
    const apiUrl = import.meta.env.VITE_API_URL;
    const token = localStorage.getItem('accessToken');

    try {
        let response;
        
        // IF MANUAL SELECTION EXISTS -> DIRECT CREATE/UPDATE
        if (manualPilots || manualAttendants) {
            const requestBody = { 
                flight_number: flightIdToFetch,
                manual_pilots: manualPilots,
                manual_attendants: manualAttendants
            };
            response = await axios.post(
                `${apiUrl}/api/roster/create/`,
                requestBody,
                { headers: { Authorization: `Bearer ${token}` } }
            );
        } 
        // IF JUST OPENING THE PAGE -> FETCH EXISTING FIRST
        else {
            try {
                response = await axios.get(
                    `${apiUrl}/api/roster/detail/${flightIdToFetch}/`,
                    { headers: { Authorization: `Bearer ${token}` } }
                );
                console.log("✅ Existing Roster found.");
            } catch (getError) {
                if (getError.response && getError.response.status === 404) {
                    console.log("⚠️ Roster missing, creating new one...");
                    const requestBody = { flight_number: flightIdToFetch };
                    response = await axios.post(
                        `${apiUrl}/api/roster/create/`,
                        requestBody,
                        { headers: { Authorization: `Bearer ${token}` } }
                    );
                } else {
                    throw getError; 
                }
            }
        }

      const data = response.data;
      const fInfo = data.flight_info;

      setFlightDetails({
        flightNo: fInfo.number,
        date: fInfo.datetime ? new Date(fInfo.datetime).toLocaleDateString('tr-TR') : "---",
        time: fInfo.datetime ? new Date(fInfo.datetime).toLocaleTimeString('tr-TR', {hour: '2-digit', minute:'2-digit'}) : "---",
        duration: fInfo.duration || "---",
        distance: fInfo.distance || "0",
        source: { 
            code: fInfo.source?.code || "DEP", 
            city: fInfo.source?.city || "Departure", 
            airport: fInfo.source?.name || "-" 
        },
        destination: { 
            code: fInfo.destination?.code || "ARR", 
            city: fInfo.destination?.city || "Arrival", 
            airport: fInfo.destination?.name || "-" 
        },
        vehicle: { 
            type: (typeof fInfo.vehicle === 'object' && fInfo.vehicle !== null) ? fInfo.vehicle.type : fInfo.vehicle,
            seats: fInfo.capacity, 
            menu: fInfo.menu 
        },
        shared: { 
            isShared: fInfo.shared_flight?.is_shared || false,
            airline: fInfo.shared_flight?.airline || "",
            flightNumber: fInfo.shared_flight?.flight_number || ""
        }
      });

      // --- DEDUPLICATION LOGIC ---
      
      const rawPilots = data.crew
        .filter(c => c.type === 'PILOT')
        .map((p) => ({
            id: String(p.original_id),
            name: p.name, 
            role: p.role
        }));
      
      // Filter unique by ID 
      const uniquePilots = [...new Map(rawPilots.map(item => [item.id, item])).values()];

      const rawCabin = data.crew
        .filter(c => c.type === 'CABIN')
        .map((c) => ({
            id: String(c.original_id),
            name: c.name, 
            role: c.role
        }));

      // Filter unique by ID
      const uniqueCabin = [...new Map(rawCabin.map(item => [item.id, item])).values()];

      setPilots(uniquePilots);
      setCabinCrew(uniqueCabin);

      const formattedPassengers = data.passengers.map(p => ({
        id: String(p.id), 
        flightId: fInfo.number,
        name: p.name,
        age: p.age,
        gender: p.gender,
        nationality: p.nationality,
        seatType: p.type === 'business' ? 'Business' : 'Economy', 
        seat: (p.seat_number === "STANDBY" || p.seat_number === "INFANT") ? null : p.seat_number,
        affiliatedIds: p.affiliated_passengers || [], 
        parentId: p.parent_id
      }));

      const uniquePassengers = [...new Map(formattedPassengers.map(item => [item.id, item])).values()];
      setPassengers(uniquePassengers);

    } catch (error) {
      console.error("Roster Error:", error);
      if (error.response && error.response.status === 401) {
          alert("Session expired. Please login again.");
          navigate('/login');
      } else {
          alert("Error: Could not fetch data.");
      }
    } finally {
      setLoading(false);
    }
  };
  

  // --- 2. FETCH AVAILABLE CANDIDATES ---
  const fetchAvailableCrew = async (roleType) => {
    try {
        const apiUrl = import.meta.env.VITE_API_URL;
        const token = localStorage.getItem('accessToken');
        
        const response = await axios.get(
            `${apiUrl}/api/available-crew/?flight_number=${flightDetails.flightNo}`,
            { headers: { Authorization: `Bearer ${token}` } }
        );

        const data = response.data;
        let candidates = [];

        if (roleType === 'pilot') {
            candidates = data.pilots.map(p => ({
                id: p.pilot_id,
                name: p.full_name,
                vehicleRestriction: p.vehicle_types && p.vehicle_types.length > 0 ? p.vehicle_types[0] : "",
                allowedRange: parseFloat(p.allowed_range),
                seniority: p.seniority_level,
                status: "Available",
                age: p.age,
                nationality: p.nationality,
                type: 'Pilot'
            }));
        } else {
            candidates = data.attendants.map(a => ({
                id: a.attendant_id,
                name: a.full_name,
                vehicleRestrictions: a.vehicle_types || [],
                type: a.attendant_type,
                status: "Available",
                recipes: a.known_recipes || []
            }));
        }
        setAvailableCandidates(candidates);
    } catch (error) {
        console.error("Available Crew Error:", error);
        alert("Could not fetch available staff list.");
    }
  };

  useEffect(() => {
    if (location.state && location.state.selectedFlightId) {
        fetchRosterData(location.state.selectedFlightId);
    }
  }, [location]);

  // --- MODAL MANAGEMENT ---
  const [switchModal, setSwitchModal] = useState({ isOpen: false, role: null, index: null });

  const handleOpenSwitchModal = async (role, index) => {
    await fetchAvailableCrew(role);
    setSwitchModal({ isOpen: true, role, index });
  };

  const handleAssignNewCrew = async (newPerson) => {
    const { role, index } = switchModal;
    
    // --- RULE 1: PILOT SAFETY CHECK (CANNOT BE 2 JUNIORS) ---
    if (role === 'pilot') {
        const otherPilotIndex = index === 0 ? 1 : 0;
        const otherPilot = pilots[otherPilotIndex];

        const newRank = (newPerson.seniority || "").toUpperCase();
        const otherRank = (otherPilot?.role || "").toUpperCase();

        if (newRank === 'JUNIOR' && otherRank === 'JUNIOR') {
            alert("⚠️ Safety Violation: Cockpit cannot have two Junior pilots!");
            return; 
        }
    }

    // --- RULE 2: CABIN CREW SAFETY CHECK (AT LEAST 1 CHIEF) ---
    if (role === 'cabin') {
        const leavingPerson = cabinCrew[index];
        
        const leavingRole = (leavingPerson.role || "").toUpperCase();
        const enteringRole = (newPerson.type || "").toUpperCase();

        // Count total Chiefs currently in list
        const currentChiefCount = cabinCrew.filter(c => (c.role || "").toUpperCase() === 'CHIEF').length;

        // IF: Leaving person is CHIEF AND Entering person is NOT CHIEF AND Only 1 Chief remains
        if (leavingRole === 'CHIEF' && enteringRole !== 'CHIEF' && currentChiefCount <= 1) {
            alert("⚠️ Safety Violation: There must be at least one CHIEF (Senior) cabin crew member on board!");
            return; 
        }
    }

    // --- UPDATE PROCESS ---
    let currentPilotIds = pilots.map(p => String(p.id));
    let currentCabinIds = cabinCrew.map(c => String(c.id));

    if (role === 'pilot') {
        currentPilotIds[index] = String(newPerson.id);
    } else {
        currentCabinIds[index] = String(newPerson.id);
    }

    const apiUrl = import.meta.env.VITE_API_URL;
    const token = localStorage.getItem('accessToken');

    try {
        if (role === 'pilot') {
            const res = await axios.post(
                `${apiUrl}/api/roster/update-pilots/`,
                {
                    flight_number: flightDetails.flightNo,
                    pilot_ids: currentPilotIds 
                },
                { headers: { Authorization: `Bearer ${token}` } }
            );

            const rawNewPilots = res.data.current_pilots.map(p => ({
                id: String(p.original_id),
                name: p.name,
                role: p.role
            }));
            const uniqueNewPilots = [...new Map(rawNewPilots.map(item => [item.id, item])).values()];
            
            setPilots(uniqueNewPilots);
            alert("✅ Pilot changed successfully!");

        } else {
            fetchRosterData(flightDetails.flightNo, currentPilotIds, currentCabinIds);
        }
        setSwitchModal({ isOpen: false, role: null, index: null });
    } catch (error) {
        console.error("Update Error:", error);
        if (error.response && error.response.data && error.response.data.details) {
            const errorMsg = Array.isArray(error.response.data.details) 
                ? error.response.data.details.join("\n") 
                : error.response.data.details;
            alert(`Update Failed:\n${errorMsg}`);
        } else {
            alert("An error occurred while updating.");
        }
    }
  };

  // --- SAVE FUNCTION ---
  const handleDatabaseSave = async () => {
    try {
      const apiUrl = import.meta.env.VITE_API_URL;
      const token = localStorage.getItem('accessToken');

      const response = await axios.post(
        `${apiUrl}/api/roster/save-selection/`,
        {
          flight_number: flightDetails.flightNo,
          db_type: 'NOSQL' 
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      alert(`✅ ${response.data.message}`);

    } catch (error) {
      console.error("Save Error:", error);
      alert("Error: Save operation failed.");
    }
  };

  // --- JSX ---
  return (
    <div className="roster-page">

      <div style={{ marginBottom: '15px' }}>
        <button 
            onClick={() => navigate('/')}
            style={{
                display: 'flex', alignItems: 'center', gap: '5px', 
                background: 'none', border: 'none', cursor: 'pointer', 
                color: '#666', fontSize: '1rem', fontWeight: '500'
            }}
        >
            <ArrowLeft size={20} /> Back to Flights
        </button>
      </div>

      <div className="flight-detail-card">
        <div className="detail-row top-row">
          <div className="flight-identity">
            <span className="flight-no-label">Flight No</span>
            {loading ? <Loader className="spin" /> : <h1 className="flight-no-val">{flightDetails.flightNo}</h1>}
            
            {/* --- SHARED FLIGHT WARNING --- */}
            {flightDetails.shared && flightDetails.shared.isShared && (
                <div style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '6px', 
                    marginTop: '8px', 
                    color: '#e65100',      
                    fontSize: '0.85rem',
                    fontWeight: '600',
                    backgroundColor: '#fff3e0', 
                    padding: '4px 8px',
                    borderRadius: '6px',
                    width: 'fit-content'
                }}>
                    <Info size={14} />
                    <span>
                        Shared by <strong>{flightDetails.shared.airline}</strong> ({flightDetails.shared.flightNumber})
                    </span>
                </div>
            )}

          </div>
          
          <div className="flight-schedule">
            <div className="schedule-item">
              <Calendar size={16} className="icon-muted" /> {flightDetails.date}
            </div>
            <div className="schedule-item">
              <Clock size={16} className="icon-muted" /> {flightDetails.time}
            </div>
          </div>
        </div>

        <hr className="card-divider" />

        <div className="detail-row route-row">
          <div className="location-box text-left">
            <div className="airport-code">{flightDetails.source.code}</div>
            <div className="city-name">{flightDetails.source.city}</div>
            <div className="airport-name">{flightDetails.source.airport}</div>
          </div>

          <div className="route-visual">
            <span className="route-duration">{flightDetails.duration}</span>
            <div className="visual-line"></div>
            <Plane size={24} className="visual-plane" />
            <div className="visual-line"></div>
          </div>

          <div className="location-box text-right">
            <div className="airport-code">{flightDetails.destination.code}</div>
            <div className="city-name">{flightDetails.destination.city}</div>
            <div className="airport-name">{flightDetails.destination.airport}</div>
          </div>
        </div>

        <div className="detail-footer">
          <div className="footer-item">
            <Plane size={16} /> 
            <span><strong>Vehicle:</strong> {flightDetails.vehicle.type} ({flightDetails.vehicle.seats} Seats)</span>
          </div>
          <div className="footer-item">
            <MapPin size={16} /> 
            <span><strong>Distance:</strong> {flightDetails.distance} km</span>
          </div>
          <div className="footer-item">
            <Utensils size={16} /> 
            <span><strong>Menu:</strong> {flightDetails.vehicle.menu}</span>
          </div>
        </div>
      </div>

      <div className="roster-grid">
        <CrewPanel 
            pilots={pilots} 
            cabinCrew={cabinCrew} 
            onSwitchClick={handleOpenSwitchModal} 
            onSaveClick={handleDatabaseSave}
        />
        <PassengerPanel passengers={passengers} onPassengerClick={setSelectedPassenger} />
      </div>

      <div className="panel-container airplane-view-panel">
        <h3 className="panel-title">Airplane View</h3>
        <div className="airplane-graphic-container">
            <AirplaneView 
                passengers={passengers} 
                pilots={pilots}       
                cabinCrew={cabinCrew}
                vehicleType={flightDetails.vehicle.type}
            />
        </div>
      </div>

      <PassengerModal passenger={selectedPassenger} onClose={() => setSelectedPassenger(null)} onUpdate={() => fetchRosterData(flightDetails.flightNo)} />

      <CrewSwitchModal 
        isOpen={switchModal.isOpen}
        role={switchModal.role}
        onClose={() => setSwitchModal({ ...switchModal, isOpen: false })}
        onAssign={handleAssignNewCrew}
        candidates={availableCandidates} 
        assignedIds={
            switchModal.role === 'pilot' 
                ? pilots.map(p => String(p.id)) 
                : cabinCrew.map(c => String(c.id))
        }
        flightRequirements={{
            vehicleType: flightDetails.vehicle.type,
            distance: parseFloat(flightDetails.distance)
        }} 
      />

    </div>
  );
}

export default Roster;