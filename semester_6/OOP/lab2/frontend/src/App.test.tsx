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

  it('renders admin publication edit controls', async () => {
    localStorage.setItem('periodicals.jwt', 'admin-token');
    localStorage.setItem('periodicals.user', JSON.stringify({ id: 1, username: 'admin', role: 'admin' }));
    vi.stubGlobal('fetch', vi.fn(async () => new Response(JSON.stringify([
      { id: 1, title: 'Наука і життя', publisher: 'Українська преса', period_months: 1, price: '120.00' }
    ]), { status: 200, headers: { 'Content-Type': 'application/json' } })));

    renderApp('/publications');

    expect(await screen.findByRole('button', { name: 'Редагувати' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Видалити' })).toBeInTheDocument();
  });

  it('renders subscription month editor and payment status controls', async () => {
    localStorage.setItem('periodicals.jwt', 'reader-token');
    localStorage.setItem('periodicals.user', JSON.stringify({ id: 2, username: 'reader', role: 'reader' }));
    vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL) => {
      const url = input.toString();
      const body = url.includes('/payments')
        ? [{ id: 5, subscription_id: 7, amount: '240.00', status: 'registered' }]
        : [{
          id: 7,
          user_id: 2,
          publication_id: 1,
          months: 2,
          total_amount: '240.00',
          status: 'created',
          publication: { id: 1, title: 'Наука і життя', publisher: 'Українська преса', period_months: 1, price: '120.00' }
        }];
      return new Response(JSON.stringify(body), { status: 200, headers: { 'Content-Type': 'application/json' } });
    }));

    renderApp('/subscriptions');
    expect(await screen.findByRole('button', { name: 'Оновити' })).toBeInTheDocument();

    await userEvent.click(screen.getByRole('button', { name: 'Показати платежі' }));

    expect(await screen.findByLabelText('Статус платежу 5')).toBeInTheDocument();
  });
});
