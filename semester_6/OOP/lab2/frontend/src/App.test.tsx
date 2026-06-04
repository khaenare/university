import { cleanup, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { afterEach, describe, expect, it, vi } from 'vitest';
import App from './App';
import { AuthProvider } from './AuthContext';

function renderApp(path = '/login') {
  return render(<MemoryRouter initialEntries={[path]}><AuthProvider><App /></AuthProvider></MemoryRouter>);
}

afterEach(() => {
  cleanup();
  localStorage.clear();
  vi.restoreAllMocks();
});

describe('App routing and auth', () => {
  it('redirects protected pages to login', () => {
    renderApp('/publications');

    expect(screen.getByRole('heading', { name: 'Вхід' })).toBeInTheDocument();
  });

  it('submits login and stores jwt', async () => {
    vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL) => {
      const url = input.toString();
      const body = url.includes('/auth/login')
        ? { access_token: 'jwt-token', user: { id: 1, username: 'reader', role: 'reader' } }
        : [];
      return new Response(JSON.stringify(body), { status: 200, headers: { 'Content-Type': 'application/json' } });
    }));
    renderApp('/login');

    await userEvent.click(screen.getByRole('button', { name: 'Увійти' }));

    expect(localStorage.getItem('periodicals.jwt')).toBe('jwt-token');
  });
});
