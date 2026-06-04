import type { Payment, Publication, Subscription, User } from './types';

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api';
const TOKEN_KEY = 'periodicals.jwt';
const USER_KEY = 'periodicals.user';

export interface Session {
  accessToken: string;
  user: User;
}

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

export function saveSession(session: Session): void {
  localStorage.setItem(TOKEN_KEY, session.accessToken);
  localStorage.setItem(USER_KEY, JSON.stringify(session.user));
}

export function loadSession(): Session | null {
  const accessToken = localStorage.getItem(TOKEN_KEY);
  const rawUser = localStorage.getItem(USER_KEY);
  if (!accessToken || !rawUser) return null;
  return { accessToken, user: JSON.parse(rawUser) as User };
}

export function clearSession(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const session = loadSession();
  const headers = new Headers(options.headers);
  headers.set('Content-Type', 'application/json');
  if (session) headers.set('Authorization', `Bearer ${session.accessToken}`);
  const response = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new ApiError(response.status, body.detail ?? 'Request failed');
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export async function login(username: string, password: string): Promise<Session> {
  const response = await request<{ access_token: string; user: User }>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password })
  });
  const session = { accessToken: response.access_token, user: response.user };
  saveSession(session);
  return session;
}

export const api = {
  publications: () => request<Publication[]>('/publications'),
  createPublication: (publication: Omit<Publication, 'id'>) => request<Publication>('/publications', { method: 'POST', body: JSON.stringify(publication) }),
  updatePublication: (id: number, publication: Omit<Publication, 'id'>) => request<Publication>(`/publications/${id}`, { method: 'PUT', body: JSON.stringify(publication) }),
  deletePublication: (id: number) => request<void>(`/publications/${id}`, { method: 'DELETE' }),
  subscriptions: () => request<Subscription[]>('/subscriptions'),
  createSubscription: (publicationId: number, months: number) => request<Subscription>('/subscriptions', { method: 'POST', body: JSON.stringify({ publication_id: publicationId, months }) }),
  updateSubscription: (id: number, months: number) => request<Subscription>(`/subscriptions/${id}`, { method: 'PUT', body: JSON.stringify({ months }) }),
  deleteSubscription: (id: number) => request<void>(`/subscriptions/${id}`, { method: 'DELETE' }),
  payments: (subscriptionId: number) => request<Payment[]>(`/subscriptions/${subscriptionId}/payments`),
  createPayment: (subscriptionId: number, amount: string) => request<Payment>(`/subscriptions/${subscriptionId}/payments`, { method: 'POST', body: JSON.stringify({ amount }) }),
  updatePayment: (id: number, status: string) => request<Payment>(`/payments/${id}`, { method: 'PUT', body: JSON.stringify({ status }) }),
  deletePayment: (id: number) => request<void>(`/payments/${id}`, { method: 'DELETE' })
};
