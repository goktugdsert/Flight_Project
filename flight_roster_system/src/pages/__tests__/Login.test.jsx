import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import axios from 'axios';
import Login from '../login';

// 1. Mock necessary libraries
vi.mock('axios');

const mockedNavigate = vi.fn();

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockedNavigate,
  };
});

vi.stubGlobal('import.meta', { env: { VITE_API_URL: 'http://mock-api.com' } });

describe('Login Component Tests', () => {
  
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('should login successfully with correct credentials', async () => {
    // --- ARRANGE ---
    // Make axios return success (200 OK)
    axios.post.mockResolvedValueOnce({
      data: {
        access: 'fake-access-token',
        refresh: 'fake-refresh-token'
      }
    });

    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );

    // --- ACT ---
    // Fill in username and password
    const usernameInput = screen.getByLabelText(/Username/i);
    const passwordInput = screen.getByLabelText(/Password/i);
    const loginButton = screen.getByRole('button', { name: /Login/i });

    fireEvent.change(usernameInput, { target: { value: 'admin' } });
    fireEvent.change(passwordInput, { target: { value: '123456' } });

    fireEvent.click(loginButton);

    // --- ASSERT ---
    await waitFor(() => {
      // Was axios called with correct url and data?
      expect(axios.post).toHaveBeenCalledWith(
        'http://localhost:8001/api/token/',
        { username: 'admin', password: '123456' }
      );

      // Is the token saved to localStorage?
      expect(localStorage.getItem('accessToken')).toBe('fake-access-token');

      // Did it redirect to home page ("/")?
      expect(mockedNavigate).toHaveBeenCalledWith('/');
    });
  });

  it('should show error message when login fails (401)', async () => {
    // --- ARRANGE ---
    // Make axios return error (401 Unauthorized)
    axios.post.mockRejectedValueOnce({
      response: { status: 401 }
    });

    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );

    // --- ACT ---
    fireEvent.change(screen.getByLabelText(/Username/i), { target: { value: 'wrongUser' } });
    fireEvent.change(screen.getByLabelText(/Password/i), { target: { value: 'wrongPass' } });
    fireEvent.click(screen.getByRole('button', { name: /Login/i }));

    // --- ASSERT ---
    await waitFor(() => {
      expect(screen.getByText('Username or password incorrect!')).toBeInTheDocument();
    });

    expect(localStorage.getItem('accessToken')).toBeNull();
    expect(mockedNavigate).not.toHaveBeenCalled();
  });
});