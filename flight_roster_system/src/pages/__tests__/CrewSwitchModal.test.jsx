import { render, screen, fireEvent } from '@testing-library/react';
import { vi, describe, it, expect } from 'vitest';
import CrewSwitchModal from '../../CrewSwitchModal'; 

describe('CrewSwitchModal Component Tests', () => {
  it('should render candidates and handle assignment selection', () => {
    // 1. Mock Data
    const mockOnAssign = vi.fn();
    const mockCandidates = [
      {
        id: '999',
        name: 'Top Gun Maverick',
        seniority: 'SENIOR',
        status: 'Available',
        vehicleRestriction: 'Boeing 737'
      }
    ];

    // 2. Render
    render(
      <CrewSwitchModal 
        isOpen={true}
        role="pilot"
        candidates={mockCandidates}
        onClose={() => {}}
        onAssign={mockOnAssign}
        assignedIds={[]} 
        flightRequirements={{ vehicleType: 'Boeing 737' }}
      />
    );

    // 3. Is the name visible on screen?
    expect(screen.getByText('Top Gun Maverick')).toBeInTheDocument();

    // 4. Click the "Assign" button
    const assignBtn = screen.getByText('Assign');
    fireEvent.click(assignBtn);

    // 5. Was the function triggered?
    expect(mockOnAssign).toHaveBeenCalledTimes(1);
    // Was it called with the correct params? (The selected person)
    expect(mockOnAssign).toHaveBeenCalledWith(expect.objectContaining({ name: 'Top Gun Maverick' }));
  });

  it('should disable button if candidate is already assigned', () => {
    const mockCandidates = [
      { id: '123', name: 'Already There', vehicleRestriction: 'Boeing 737' }
    ];

    render(
      <CrewSwitchModal 
        isOpen={true}
        candidates={mockCandidates}
        onClose={() => {}}
        onAssign={() => {}}
        assignedIds={['123']} 
        flightRequirements={{ vehicleType: 'Boeing 737' }}
      />
    );

    // Button text should be 'Active' and it must be disabled
    const btn = screen.getByText('Active');
    expect(btn).toBeDisabled();
  });
});