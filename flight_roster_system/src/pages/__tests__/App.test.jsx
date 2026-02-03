import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { vi, describe, it, expect } from 'vitest';
import App from '../../App'; 

const mockNavigate = vi.fn();

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

describe('App Layout & Navigation Tests', () => {

  it('should render sidebar and handle navigation clicks', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );

    // 1. Are the buttons in the sidebar visible on screen?
    expect(screen.getByText('Home')).toBeInTheDocument();
    expect(screen.getByText('Pilots')).toBeInTheDocument();
    expect(screen.getByText('Cabin Crew')).toBeInTheDocument();

    // 2. Click the "Pilots" button
    fireEvent.click(screen.getByText('Pilots'));
    // Did it redirect to the '/pilots' page?
    expect(mockNavigate).toHaveBeenCalledWith('/pilots');

    // 3. Click the "Saved Rosters" button
    fireEvent.click(screen.getByText('Saved Rosters'));
    expect(mockNavigate).toHaveBeenCalledWith('/saved-rosters');
  });

  it('should toggle sidebar open/close class', () => {
    // using the container object to check DOM element classes
    const { container } = render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );

    // Sidebar element ('aside' tag)
    const sidebar = container.querySelector('aside');
    
    // Toggle button (the one with the Menu icon)
    const toggleBtn = container.querySelector('.toggle-btn');

    // 1. Sidebar should be closed initially (NO 'open' class)
    expect(sidebar.classList.contains('open')).toBe(false);

    // 2. Click the toggle button
    fireEvent.click(toggleBtn);

    // 3. Now the sidebar should be open (HAS 'open' class)
    expect(sidebar.classList.contains('open')).toBe(true);

    // 4. Click again
    fireEvent.click(toggleBtn);

    // 5. Should close again
    expect(sidebar.classList.contains('open')).toBe(false);
  });

  it('should handle logout', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );

    const exitBtn = screen.getByText('Exit');
    
    fireEvent.click(exitBtn);

    // Did it redirect to the login page?
    expect(mockNavigate).toHaveBeenCalledWith('/login');
  });
});