import { render, screen, fireEvent } from '@testing-library/react';
import { vi, describe, it, expect } from 'vitest';
import PassengerPanel from '../../PassengerPanel'; 

describe('PassengerPanel Component Tests', () => {
  
  // Mock Passenger Data
  const mockPassengers = [
    { id: '101', name: 'John Doe', seat: '1A', parentId: null, age: 30 },
    { id: '102', name: 'Baby Doe', seat: null, parentId: '101', age: 1 } // Baby linked to John
  ];

  it('should render passengers and filter by search term', () => {
    render(
      <PassengerPanel 
        passengers={mockPassengers} 
        onPassengerClick={() => {}} 
      />
    );

    // 1. Are both visible initially?
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('Baby Doe')).toBeInTheDocument();

    // 2. Type "Baby" into the search box
    const searchInput = screen.getByPlaceholderText('Search...');
    fireEvent.change(searchInput, { target: { value: 'Baby' } });

    // 3. John Doe should disappear, Baby Doe should stay
    expect(screen.queryByText('John Doe')).not.toBeInTheDocument();
    expect(screen.getByText('Baby Doe')).toBeInTheDocument();
  });

  it('should handle row click and link icon click independently', () => {
    const mockOnPassengerClick = vi.fn();
    
    const alertMock = vi.spyOn(window, 'alert').mockImplementation(() => {});

    render(
      <PassengerPanel 
        passengers={mockPassengers} 
        onPassengerClick={mockOnPassengerClick} 
      />
    );

    // --- SCENARIO 1: ROW CLICK ---
    // Click on John Doe row
    fireEvent.click(screen.getByText('John Doe'));
    expect(mockOnPassengerClick).toHaveBeenCalledTimes(1);
    // Called with which data?
    expect(mockOnPassengerClick).toHaveBeenCalledWith(expect.objectContaining({ name: 'John Doe' }));


    // --- SCENARIO 2: ICON CLICK (STOP PROPAGATION) ---
    // Baby Doe should have a Link icon (since parentId exists)
    // We can find the 'span' element wrapping the icon via its title attribute
    const linkIcon = screen.getByTitle('Click to see connections');
    
    fireEvent.click(linkIcon);

    // EXPECTATIONS:
    // 1. Alert should open
    expect(alertMock).toHaveBeenCalled();
    // 2. Row click function (mockOnPassengerClick) should NOT be called again
    expect(mockOnPassengerClick).toHaveBeenCalledTimes(1);

    alertMock.mockRestore();
  });
});