import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios'; 
import { Plane, User, Users, FileText, Search, ArrowRight, Calendar, MapPin, Info, Sliders, Loader } from 'lucide-react';
import './home.css'; 

// --- DASHBOARD CARD COMPONENT ---
const DashboardCard = ({ title, value, icon, colorClass, iconColor }) => {
  let bgColor = '#f0f9ff'; 
  let textColor = '#0369a1';

  if (colorClass.includes('purple')) { bgColor = '#f3e8ff'; textColor = '#7e22ce'; }
  if (colorClass.includes('orange')) { bgColor = '#ffedd5'; textColor = '#c2410c'; }
  
  return (
    <div className="stat-card">
      <div className="stat-info">
        <p className="stat-title">{title}</p>
        <h3 className="stat-value">{value}</h3>
      </div>
      <div className="stat-icon-box" style={{ backgroundColor: bgColor, color: textColor }}>
        {icon}
      </div>
    </div>
  );
};

const Home = () => {
  const navigate = useNavigate();

  // --- STATE DEFINITIONS ---
  const [allFlights, setAllFlights] = useState([]); 
  const [flights, setFlights] = useState([]);       
  const [loading, setLoading] = useState(true);     
  const [error, setError] = useState(null);         

  // STATE FOR DASHBOARD STATISTICS
  const [stats, setStats] = useState({
    activeCrew: 0,
    savedRosters: 0
  });

  const [filters, setFilters] = useState({ flightNo: '', source: '', destination: '', date: '' });
  
  // Filter options
  const sources = [...new Set(allFlights.map(f => f.source))];
  const destinations = [...new Set(allFlights.map(f => f.destination))];

  const totalFlightsCount = allFlights.length;

  // --- 1. FETCHING DATA FROM BACKEND ---
  useEffect(() => {
    const fetchData = async () => {
      try {
        const apiUrl = import.meta.env.VITE_API_URL;
        const token = localStorage.getItem('accessToken');
        const headers = { Authorization: `Bearer ${token}` };

        // PARALLEL REQUEST: Fetching flights and stats simultaneously
        // 
        const [flightsRes, statsRes] = await Promise.all([
            axios.get(`${apiUrl}/api/flights/`, { headers }),
            axios.get(`${apiUrl}/api/roster/dashboard-stats/`, { headers })
        ]);

        // A. Processing Flight Data
        const rawData = flightsRes.data;
        const flightList = Array.isArray(rawData) ? rawData : (rawData.results || []);

        // 
        const formattedData = flightList.map(flight => {
          const sourceCode = flight.flight_source?.code || flight.source || "???";
          const destCode = flight.flight_destination?.code || flight.destination || "???";
          const planeName = flight.vehicle_type?.name || "Unknown Plane";
          const rawDate = flight.flight_datetime || flight.departure_time;
          let finalDateString = "No Date";
          if (rawDate) {
              const d = new Date(rawDate);
              const datePart = d.toLocaleDateString('en-GB'); // dd/mm/yyyy
              const timePart = d.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', hour12: false }); // HH:mm
              finalDateString = `${datePart} - ${timePart}`; // Added a hyphen in between
          }

          return {
            id: flight.flight_number, 
            source: sourceCode,
            destination: destCode,
            route: `${sourceCode} - ${destCode}`,
            date: finalDateString, 
            planeType: planeName,
            passengers: flight.passenger_count || 0, 
            crew: 0 
          };
        });

        setAllFlights(formattedData);
        setFlights(formattedData); 

        // B. Processing Stats Data
        setStats({
            activeCrew: statsRes.data.total_active_crew || 0,
            savedRosters: statsRes.data.saved_rosters_count || 0
        });

        setLoading(false);

      } catch (err) {
        console.error("Error:", err);
        setError("Error occurred while fetching data.");
        setLoading(false);
      }
    };

    fetchData();
  }, []); 

  // --- 2. FILTERING LOGIC ---
  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  // 
  useEffect(() => {
    let result = allFlights;
    if (filters.flightNo) result = result.filter(f => f.id.toLowerCase().includes(filters.flightNo.toLowerCase()));
    if (filters.source) result = result.filter(f => f.source === filters.source);
    if (filters.destination) result = result.filter(f => f.destination === filters.destination);
    if (filters.date) result = result.filter(f => f.date.includes(filters.date));
    setFlights(result);
  }, [filters, allFlights]);

  // --- 3. GO TO ROSTER PAGE ---
  const handleGoToRoster = (flightId) => {
    navigate('/roster', { state: { selectedFlightId: flightId } });
  };

  // --- SCREEN STATES ---
  if (loading) return (
    <div className="home-dashboard" style={{display:'flex', justifyContent:'center', alignItems:'center', height:'100vh'}}>
      <div style={{textAlign:'center'}}>
        <Loader className="spin" size={40} color="#0369a1"/>
        <p>Loading Dashboard...</p>
      </div>
    </div>
  );

  if (error) return (
    <div className="home-dashboard" style={{padding:'40px', color:'red', textAlign:'center'}}>
      <h3>⚠️ Error Occurred</h3>
      <p>{error}</p>
    </div>
  );

  return (
    <div className="home-dashboard">
      
      <div className="stats-grid">
        {/* Total Flight: Comes from list length */}
        <DashboardCard 
            title="Total Flight" 
            value={totalFlightsCount} 
            icon={<Plane size={24} />} 
            colorClass="bg-blue-50" 
            iconColor="text-blue-700"
        />
        
        {/* Active Crew: Comes from Backend (RosterCrew Count) */}
        <DashboardCard 
            title="Active Crew" 
            value={stats.activeCrew} 
            icon={<User size={24} />} 
            colorClass="bg-purple-50" 
            iconColor="text-purple-700"
        />
        
        {/* Saved Rosters: Comes from Backend (JSON File Count) */}
        <DashboardCard 
            title="Saved Rosters" 
            value={stats.savedRosters} 
            icon={<FileText size={24} />} 
            colorClass="bg-orange-50" 
            iconColor="text-orange-700"
        />
      </div>

      <div className="search-section">
        <h2 className="section-title"><Search size={20} /> Search Flights</h2>
        <div className="filter-grid">
          <div className="filter-group"><label>FLIGHT NO</label><input type="text" name="flightNo" placeholder="TK..." value={filters.flightNo} onChange={handleFilterChange} className="main-search-input" /></div>
          <div className="filter-group"><label>FROM</label><select name="source" value={filters.source} onChange={handleFilterChange} className="main-search-input"><option value="">All Locations</option>{sources.map(s => <option key={s} value={s}>{s}</option>)}</select></div>
          <div className="filter-group"><label>TO</label><select name="destination" value={filters.destination} onChange={handleFilterChange} className="main-search-input"><option value="">All Locations</option>{destinations.map(d => <option key={d} value={d}>{d}</option>)}</select></div>
          <div className="filter-group"><label>DATE</label><input type="text" name="date" placeholder="dd.mm.yyyy" value={filters.date} onChange={handleFilterChange} className="main-search-input" /></div>
          <div className="filter-group filter-btn-group"><button className="filter-btn">Filter</button></div>
        </div>
      </div>

      <div className="flight-list-container">
        <div className="list-header">
          <div className="col"><Plane size={16} /> Flight No</div>
          <div className="col"><MapPin size={16} /> Route</div>
          <div className="col"><Calendar size={16} /> Date</div>
          <div className="col"><Info size={16} /> Info</div>
          <div className="col justify-center"><Sliders size={16} /> Action</div>
        </div>
        
        <div className="list-body">
          {flights.length > 0 ? (
            flights.map((flight) => (
              <div key={flight.id} className="list-row">
                <div className="col font-bold">{flight.id}</div>
                <div className="col">{flight.route}</div>
                <div className="col text-muted">{flight.date}</div>
                
                <div className="col text-muted text-small">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '5px', flexWrap: 'wrap' }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><Plane size={14} /> {flight.planeType}</span>
                    <span>-</span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><Users size={14} /> Pass: {flight.passengers}</span>
                  </div>
                </div>

                <div className="col align-right">
                  <button onClick={() => handleGoToRoster(flight.id)} className="view-roster-btn">
                    view roster <ArrowRight size={14} />
                  </button>
                </div>
              </div>
            ))
          ) : (
             <div style={{padding: '20px', textAlign: 'center', color: '#888'}}>No flights found.</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Home;