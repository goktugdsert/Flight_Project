import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { vi, describe, it, expect } from 'vitest';
import axios from 'axios';
import Home from '../home';

vi.mock('axios');

// stubbing env variables to prevent VITE_API_URL errors during test
vi.stubGlobal('import.meta', { env: { VITE_API_URL: 'http://mock-api.com' } });

describe('Home Page Tests', () => {
  it('should render flights after API call', async () => {
    // 1. Mock Data
    const mockFlights = [
      {
        flight_number: 'TK123',
        source: 'IST',
        destination: 'LHR',
        flight_datetime: '2025-10-10T10:00:00',
        vehicle_type: { name: 'Boeing 737' },
        passenger_count: 150
      }
    ];

    const mockStats = {
      total_active_crew: 5,
      saved_rosters_count: 2
    };

    // configure axios to return this data when called
    axios.get.mockResolvedValueOnce({ data: mockFlights }); // first call (flights)
    axios.get.mockResolvedValueOnce({ data: mockStats });   // second call (stats)

    // 2. Render the component
    render(
      <BrowserRouter>
        <Home />
      </BrowserRouter>
    );

    // 3. check if "Loading" text is present initially
    expect(screen.getByText(/Loading/i)).toBeInTheDocument();

    // 4. wait for loading to finish and data to appear
    await waitFor(() => {
        // is the flight number visible?
        expect(screen.getByText('TK123')).toBeInTheDocument();
        // is the route visible?
        expect(screen.getByText('IST - LHR')).toBeInTheDocument();
    });
  });
});