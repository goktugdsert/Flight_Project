import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import AirplaneView from '../../AirplaneView'; 

describe('AirplaneView Component Tests', () => {
  
  // Mock Passengers
  const mockPassengers = [
    { name: 'Passenger 1', seat: '1A' }, // Business
    { name: 'Passenger 2', seat: '10A' } // Economy
  ];

  // Mock Pilots
  const mockPilots = [
    { name: 'Captain Pilot', id: 'P1' },
    { name: 'First Officer', id: 'P2' }
  ];

  it('should render correct number of pilots and passenger seats', () => {
    // 1. Render (Boeing 737)
    render(
      <AirplaneView 
        vehicleType="Boeing 737"
        passengers={mockPassengers}
        pilots={mockPilots}
        cabinCrew={[]}
      />
    );

    // 2. Are pilot seats (P1 and P2) on screen?
    // The component renders pilot seats with the letter "P".
    // If occupied, they hold data for the tooltip.
    const pilotSeats = screen.getAllByText('P');
    expect(pilotSeats.length).toBeGreaterThanOrEqual(2);

    // 3. Are passenger seats (1A and 10A) on screen?
    expect(screen.getByText('1A')).toBeInTheDocument();
    expect(screen.getByText('10A')).toBeInTheDocument();
  });

  it('should show tooltip when a seated passenger is clicked', () => {
    render(
      <AirplaneView 
        passengers={mockPassengers}
        pilots={[]}
        cabinCrew={[]}
      />
    );

    // 1. Find the occupied seat 1A
    const seat1A = screen.getByText('1A');

    // 2. Click the seat
    fireEvent.click(seat1A);

    // 3. Is the tooltip open? (Passenger name should be visible)
    expect(screen.getByText('Passenger 1')).toBeInTheDocument();
    
    // 4. Click the close button (X icon) inside tooltip
    const closeBtn = screen.getByRole('button');
    fireEvent.click(closeBtn);

    // 5. Is the tooltip closed? 
    expect(screen.queryByText('Passenger 1')).not.toBeInTheDocument();
  });
});