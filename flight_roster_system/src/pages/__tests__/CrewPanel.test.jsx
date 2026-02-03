import { render, screen, fireEvent } from '@testing-library/react';
import { vi, describe, it, expect } from 'vitest';
import CrewPanel from '../../CrewPanel'; 

describe('CrewPanel Component Tests', () => {
  
  // Mock Data Sets
  const mockPilots = [
    { name: 'Captain Ali', role: 'Captain' },
    { name: 'Pilot Veli', role: 'First Officer' }
  ];

  const mockCabinCrew = [
    { name: 'Attendant Ayse', role: 'Senior' },
    { name: 'Attendant Fatma', role: 'Junior' }
  ];

  it('should render pilot and cabin crew lists correctly', () => {
    // Render the component 
    render(
      <CrewPanel 
        pilots={mockPilots} 
        cabinCrew={mockCabinCrew} 
        onSwitchClick={() => {}} 
        onSaveClick={() => {}} 
      />
    );

    // 1. Are names visible on the screen?
    expect(screen.getByText('Captain Ali')).toBeInTheDocument();
    expect(screen.getByText('Attendant Ayse')).toBeInTheDocument();

    // 2. Are role details visible inside parentheses?
    expect(screen.getByText('(Captain)')).toBeInTheDocument();
    expect(screen.getByText('(Senior)')).toBeInTheDocument();
  });

  it('should trigger correct functions when buttons are clicked', () => {
    // Mocking the functions (Spy)
    const mockOnSwitch = vi.fn();
    const mockOnSave = vi.fn();

    render(
      <CrewPanel 
        pilots={mockPilots} 
        cabinCrew={mockCabinCrew} 
        onSwitchClick={mockOnSwitch} 
        onSaveClick={mockOnSave} 
      />
    );

    // --- SAVE BUTTON TEST ---
    const saveButton = screen.getByText('Save Roster');
    fireEvent.click(saveButton);
    expect(mockOnSave).toHaveBeenCalledTimes(1);

    // --- SWITCH BUTTON TEST ---
    // There are multiple "Switch" buttons on screen (one for each crew member)
    const switchButtons = screen.getAllByText('Switch');
    
    fireEvent.click(switchButtons[0]);

    // Was onSwitchClick called with parameters ('pilot', 0)?
    expect(mockOnSwitch).toHaveBeenCalledWith('pilot', 0);
  });
});