import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Search, FileText, Calendar, Database, FolderOpen, Trash2, Loader, X, Copy, AlertTriangle, Download } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import './home.css'; 

const SavedRosters = () => {
  const [rosters, setRosters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  
  // State for JSON Viewing Modal
  const [jsonModalData, setJsonModalData] = useState(null); 

  const navigate = useNavigate();

  const currentUser = localStorage.getItem('username');
  const isViewOnly = currentUser === 'viewonly';

  // --- 1. FETCHING DATA ---
  // 
  const fetchSavedRosters = async () => {
    try {
      const apiUrl = import.meta.env.VITE_API_URL;
      const token = localStorage.getItem('accessToken');
      
      const response = await axios.get(`${apiUrl}/api/roster/list-saved/`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      setRosters(response.data);
    } catch (error) {
      console.error("Error fetching saved rosters:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSavedRosters();
  }, []);

  // --- 2. OPEN FILE ACTION ---
  const handleOpen = async (roster) => {
    const apiUrl = import.meta.env.VITE_API_URL;
    
    if (roster.db_type === 'SQL') {
       alert("This feature is for NoSQL files only.");
    } else if (roster.db_type === 'NOSQL') {
      const token = localStorage.getItem('accessToken');
      
      try {
        // Fetching data from Backend 
        // 
        const res = await axios.get(`${apiUrl}/api/roster/open-nosql/${roster.id}/`, {
            headers: { Authorization: `Bearer ${token}` }
        });
        
        // Push data to state and open modal 
        setJsonModalData({
            filename: roster.id,
            content: res.data
        });

      } catch (error) {
        console.error("Open Error:", error);
        alert("Failed to open JSON file.");
      }
    }
  };

  const handleDownloadJson = () => {
    if (!jsonModalData) return;

    const jsonString = JSON.stringify(jsonModalData.content, null, 4);
    
    const blob = new Blob([jsonString], { type: "application/json" });
    
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = jsonModalData.filename || "roster.json"; 
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  // --- 3. DELETE ACTION ---
  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this file permanently?')) {
        return;
    }

    try {
        const apiUrl = import.meta.env.VITE_API_URL;
        const token = localStorage.getItem('accessToken');
        
        // --- 1. SEND REQUEST TO BACKEND ---
        await axios.delete(`${apiUrl}/api/roster/delete-nosql/${id}/`, {
            headers: { Authorization: `Bearer ${token}` }
        });

        // --- 2. REMOVE FROM LIST IF SUCCESSFUL ---
        // 
        setRosters(prevRosters => prevRosters.filter(r => r.id !== id));
        

    } catch (error) {
        console.error("Delete Error:", error);
        alert("Failed to delete file from server.");
    }
  };

  // --- FILTERING LOGIC ---
  const filteredRosters = rosters.filter(r => 
    r.id.toLowerCase().includes(searchTerm.toLowerCase()) || 
    r.flight_number.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="home-dashboard">
      
      {/* HEADER AND SEARCH AREA */}
      <div className="search-section flex-between">
        <div>
          <h2 className="page-title">Saved Rosters</h2>
          <p className="page-subtitle">Drafts of previously created rosters (NoSQL JSON)</p>
        </div>
        <div className="search-wrapper-simple">
          <Search size={18} className="search-icon-simple" />
          <input 
            type="text" 
            placeholder="Search ID or Flight..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input-simple"
          />
        </div>
      </div>

      {/* LIST TABLE */}
      <div className="flight-list-container mt-20">
        <div className="list-header saved-rosters-grid">
          <div className="col">File Name</div>
          <div className="col">Flight No</div>
          <div className="col">Date Saved</div>
          <div className="col">Storage</div>
          <div className="col align-right" style={{ justifyContent: 'center', display: 'flex' }}>Actions</div>
        </div>
        
        <div className="list-body">
          {loading ? (
            <div className="empty-state"><Loader className="spin" /> Loading Rosters...</div>
          ) : filteredRosters.length > 0 ? (
            filteredRosters.map((roster) => (
              <div key={roster.id} className="list-row saved-rosters-grid">
                
                <div className="col flex-center-gap" style={{overflow:'hidden', textOverflow:'ellipsis'}}>
                  <FileText size={16} color="#888" /> 
                  <span style={{ fontWeight: 500, fontSize:'0.9rem' }}>{roster.id}</span>
                </div>
                
                <div className="col font-bold color-primary">{roster.flight_number}</div>
                
                <div className="col text-muted flex-center-gap">
                  <Calendar size={14} /> {roster.date_saved}
                </div>
                
                <div className="col">
                   <span className="badge-green" style={{backgroundColor:'#e8f5e9', color:'#2ecc71', padding:'4px 8px', borderRadius:'4px', fontSize:'0.8rem', fontWeight:'600', display:'flex', alignItems:'center', gap:'4px'}}>
                     <Database size={12} /> JSON (NoSQL)
                   </span>
                </div>

                <div className="col align-right flex-end-gap" style={{ justifyContent: 'center' }}>
                  <button onClick={() => handleOpen(roster)} className="btn-action btn-open">
                    <FolderOpen size={14} /> Open
                  </button>
                  {!isViewOnly && (
                    <button onClick={() => handleDelete(roster.id)} className="btn-action btn-delete">
                        <Trash2 size={14} /> Delete
                    </button>
                  )}
                </div>
              </div>
            ))
          ) : (
            <div className="empty-state">No saved rosters found.</div>
          )}
        </div>
      </div>

      {/* --- JSON VIEWING MODAL --- */}
      {jsonModalData && (
        <div className="modal-overlay" style={{display:'flex', alignItems:'center', justifyContent:'center', position:'fixed', top:0, left:0, width:'100%', height:'100%', backgroundColor:'rgba(0,0,0,0.5)', zIndex:1000}}>
          <div className="modal-content" style={{width:'80%', maxWidth:'800px', height:'80%', backgroundColor:'white', borderRadius:'8px', display:'flex', flexDirection:'column', overflow:'hidden'}}>
            
            {/* Modal Header */}
            <div style={{padding:'15px 20px', borderBottom:'1px solid #eee', display:'flex', justifyContent:'space-between', alignItems:'center', backgroundColor:'#f9f9f9'}}>
                <h3 style={{margin:0, fontSize:'1.1rem', display:'flex', alignItems:'center', gap:'10px', color: '#515151ff'}}>
                    <FileText size={20} color="#333"/> {jsonModalData.filename}
                </h3>
                <div style={{display:'flex', gap:'10px'}}>
                    <button 
                      onClick={handleDownloadJson} 
                      style={{border:'none', background:'none', cursor:'pointer', color:'#666'}} 
                      title="Download JSON"
                    >
                      <Download size={20}/>
                    </button>
                    <button 
                        onClick={() => {
                            navigator.clipboard.writeText(JSON.stringify(jsonModalData.content, null, 4));
                            alert("JSON copied to clipboard!");
                        }}
                        style={{border:'none', background:'none', cursor:'pointer', color:'#666'}} title="Copy JSON"
                    >
                        <Copy size={20}/>
                    </button>
                    <button onClick={() => setJsonModalData(null)} style={{border:'none', background:'none', cursor:'pointer', color:'#666'}}>
                        <X size={24}/>
                    </button>
                </div>
            </div>

            {/* Modal Body (JSON Viewer) */}
            <div style={{flex:1, overflow:'auto', padding:'20px', backgroundColor:'#282c34', color:'#abb2bf', fontSize:'14px', fontFamily:'monospace'}}>
                <pre style={{margin:0}}>
                    {JSON.stringify(jsonModalData.content, null, 4)}
                </pre>
            </div>

          </div>
        </div>
      )}

    </div>
  );
};

export default SavedRosters;