import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import axios from 'axios';
import PassengerModal from '../../PassengerModal'; 

// Mock Axios
vi.mock('axios');

describe('PassengerModal Component Tests', () => {
  
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // Test Data (Adult without a seat)
  const mockAdultPassenger = {
    id: 'P123',
    flightId: 'TK1920',
    name: 'John Doe',
    age: 30,
    gender: 'Male',
    nationality: 'US',
    seatType: 'Economy',
    seat: null, 
    parentId: null
  };

  // Test Data (Infant)
  const mockInfantPassenger = {
    ...mockAdultPassenger,
    id: 'Baby123',
    age: 1, // Infant
    parentId: 'P123'
  };

  it('should render passenger details correctly', () => {
    render(
      <PassengerModal 
        passenger={mockAdultPassenger} 
        onClose={() => {}} 
      />
    );

    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('P123')).toBeInTheDocument();
    expect(screen.getByText('Pending Assignment')).toBeInTheDocument();
  });

  it('should handle "Assign Seat" action successfully', async () => {
    const mockOnUpdate = vi.fn();
    const mockOnClose = vi.fn();

    vi.spyOn(window, 'alert').mockImplementation(() => {});

    axios.post.mockResolvedValue({ data: { success: true } });

    render(
      <PassengerModal 
        passenger={mockAdultPassenger} 
        onClose={mockOnClose} 
        onUpdate={mockOnUpdate}
      />
    );

    // 1. Click the button
    const assignBtn = screen.getByText('Assign Automatic Seat');
    fireEvent.click(assignBtn);

    // 2. Did the button switch to "Assigning..." mode?
    expect(screen.getByText('Assigning...')).toBeInTheDocument();

    // 3. Was the API call made?
    await waitFor(() => {
        expect(axios.post).toHaveBeenCalledWith(
            expect.stringContaining('/api/roster/assign-seat/'),
            { passenger_id: 'P123', flight_number: 'TK1920' },
            expect.anything()
        );
    });

    // 4. Were update and close functions called after completion?
    await waitFor(() => {
        expect(mockOnUpdate).toHaveBeenCalled();
        expect(mockOnClose).toHaveBeenCalled();
    });
  });

  it('should NOT show assign button for Infants', () => {
    render(
      <PassengerModal 
        passenger={mockInfantPassenger} 
        onClose={() => {}} 
      />
    );

    // 1. Is the Infant warning visible?
    expect(screen.getByText('Infant Passenger')).toBeInTheDocument();

    // 2. Assign button should NOT be present
    expect(screen.queryByText('Assign Automatic Seat')).not.toBeInTheDocument();
  });
});