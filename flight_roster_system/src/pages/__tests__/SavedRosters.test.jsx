import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import axios from 'axios';
import SavedRosters from '../SavedRosters';

// Mock Axios
vi.mock('axios');
vi.stubGlobal('import.meta', { env: { VITE_API_URL: 'http://localhost:8001' } });

describe('SavedRosters Component Tests', () => {
  
  beforeEach(() => {
    vi.clearAllMocks();
  });

  const mockRosters = [
    {
      id: 'roster_123.json',
      flight_number: 'TK1920',
      date_saved: '2025-12-10',
      db_type: 'NOSQL'
    }
  ];

  it('should render saved rosters and handle delete action', async () => {
    // 1. Fetch list on page load (GET request)
    axios.get.mockResolvedValueOnce({ data: mockRosters });

    // 2. Mock successful delete response (DELETE request)
    axios.delete.mockResolvedValueOnce({ status: 204 });

    // 3. Auto-confirm the browser's "Are you sure?" dialog
    const confirmSpy = vi.spyOn(window, 'confirm');
    confirmSpy.mockImplementation(() => true);

    render(
      <BrowserRouter>
        <SavedRosters />
      </BrowserRouter>
    );

    // --- RENDER CHECK ---
    await waitFor(() => {
        expect(screen.getByText('roster_123.json')).toBeInTheDocument();
        expect(screen.getByText('TK1920')).toBeInTheDocument();
    });

    // --- DELETE ACTION ---
    const deleteBtn = screen.getByText('Delete'); 
    
    fireEvent.click(deleteBtn);

    // --- ASSERTION ---
    await waitFor(() => {
        // 1. Was confirm dialog triggered?
        expect(confirmSpy).toHaveBeenCalled();
        
        // 2. Did Axios DELETE request go to the correct URL?
        expect(axios.delete).toHaveBeenCalledWith(
            'http://localhost:8001/api/roster/delete-nosql/roster_123.json/',
            expect.anything() 
        );

        // 3. Was item removed from screen? (Should not be in document anymore)
        expect(screen.queryByText('roster_123.json')).not.toBeInTheDocument();
    });
  });

  it('should open modal and show JSON content', async () => {
    // 1. Fetch the list
    axios.get.mockResolvedValueOnce({ data: mockRosters });

    // 2. Fetch file content (Open request)
    const mockFileContent = { pilots: ['Ali', 'Veli'], flight: 'TK1920' };
    axios.get.mockResolvedValueOnce({ data: mockFileContent });

    render(
      <BrowserRouter>
        <SavedRosters />
      </BrowserRouter>
    );

    await waitFor(() => screen.getByText('roster_123.json'));

    const openBtn = screen.getByText('Open');
    fireEvent.click(openBtn);

    // --- ASSERTION ---
    await waitFor(() => {
    // There might be multiple 'roster_123.json' (one in list, one in modal header)
    // So we use 'getAllByText' and check if at least 1 exists.
    const titles = screen.getAllByText('roster_123.json');
    expect(titles.length).toBeGreaterThan(0);
    
    // Is JSON content visible?
    expect(screen.getByText(/"pilots":/)).toBeInTheDocument();
    expect(screen.getByText(/"Ali"/)).toBeInTheDocument();
});
  });

});