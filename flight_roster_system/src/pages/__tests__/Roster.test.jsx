import { describe, test, expect, vi, beforeEach } from 'vitest'; 
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import axios from 'axios';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import Roster from '../roster'; 

// 1. MOCK AXIOS 
vi.mock('axios');

// 2. MOCK DATA
const mockFlightData = {
  data: {
    flight_info: {
      number: "TK1920",
      datetime: "2025-12-15T14:30:00",
      duration: "3h 15m",
      distance: 1200,
      source: { code: "IST", city: "Istanbul", name: "Istanbul Airport" },
      destination: { code: "LHR", city: "London", name: "Heathrow Airport" },
      vehicle: { type: "Boeing 737", capacity: 180, menu: "Standard" },
      shared_flight: { is_shared: false }
    },
    crew: [
      { original_id: 1, name: "Ahmet Pilot", role: "SENIOR", type: "PILOT" },
      { original_id: 2, name: "Mehmet Pilot", role: "JUNIOR", type: "PILOT" },
      { original_id: 3, name: "Ayşe Kabin", role: "CHIEF", type: "CABIN" }
    ],
    passengers: [
      { id: 101, name: "John Doe", age: 30, gender: "M", nationality: "USA", type: "economy", seat_number: "12A" }
    ]
  }
};

describe('Roster Component Tests', () => {
  
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test('should render flight details correctly when page loads', async () => {
    axios.get.mockResolvedValue(mockFlightData);

    render(
      <MemoryRouter initialEntries={[{ pathname: '/roster', state: { selectedFlightId: 'TK1920' } }]}>
        <Routes>
            <Route path="/roster" element={<Roster />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      // Verify flight number is on screen
      expect(screen.getByText('TK1920')).toBeInTheDocument();
      
      // Verify departure and arrival cities are on screen
      expect(screen.getByText('Istanbul')).toBeInTheDocument();
      expect(screen.getByText('London')).toBeInTheDocument();
    });

    // Check if crew info is loaded
    expect(screen.getByText('Ahmet Pilot')).toBeInTheDocument();
  });

  test('should show alert when API fails', async () => {
    // If axios returns an error
    axios.get.mockRejectedValue(new Error('Network Error'));
    
    const alertMock = vi.spyOn(window, 'alert').mockImplementation(() => {});

    render(
      <MemoryRouter initialEntries={[{ pathname: '/roster', state: { selectedFlightId: 'TK1920' } }]}>
        <Routes>
            <Route path="/roster" element={<Roster />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
        expect(alertMock).toHaveBeenCalled();
    });
  });
});