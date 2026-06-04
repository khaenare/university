import { FormEvent, ReactElement, ReactNode, useEffect, useState } from 'react';
import { Link, Navigate, Route, Routes, useNavigate } from 'react-router-dom';
import { api } from './api';
import { useAuth } from './AuthContext';
import type { Payment, Publication, Subscription } from './types';

function ProtectedRoute({ children }: { children: ReactElement }) {
  const { session } = useAuth();
  return session ? children : <Navigate to="/login" replace />;
}

function Layout({ children }: { children: ReactNode }) {
  const { session, logout } = useAuth();
  const navigate = useNavigate();
  return <>
    <header className="topbar">
      <Link to="/publications">Каталог</Link>
      <Link to="/subscriptions">Передплати</Link>
      <span>{session?.user.username} ({session?.user.role})</span>
      <button onClick={() => { logout(); navigate('/login'); }}>Вийти</button>
    </header>
    <main>{children}</main>
  </>;
}

function LoginPage() {
  const { session, login } = useAuth();
  const [username, setUsername] = useState('reader');
  const [password, setPassword] = useState('password');
  const [error, setError] = useState('');
  if (session) return <Navigate to="/publications" replace />;
  async function submit(event: FormEvent) {
    event.preventDefault();
    setError('');
    try {
      await login(username, password);
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : 'Помилка входу');
    }
  }
  return <main className="login-card">
    <h1>Вхід</h1>
    <form onSubmit={submit}>
      <label>Логін<input value={username} onChange={(event) => setUsername(event.target.value)} /></label>
      <label>Пароль<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} /></label>
      {error && <p className="error">{error}</p>}
      <button type="submit">Увійти</button>
    </form>
  </main>;
}

function PublicationsPage() {
  const { session } = useAuth();
  const [publications, setPublications] = useState<Publication[]>([]);
  const [form, setForm] = useState({ title: '', publisher: '', period_months: 1, price: '0.00' });
  const [message, setMessage] = useState('');
  const refresh = () => api.publications().then(setPublications).catch((error) => setMessage(error.message));
  useEffect(() => {
    refresh();
  }, []);
  async function createPublication(event: FormEvent) {
    event.preventDefault();
    await api.createPublication(form);
    setForm({ title: '', publisher: '', period_months: 1, price: '0.00' });
    refresh();
  }
  async function subscribe(publicationId: number) {
    await api.createSubscription(publicationId, 1);
    setMessage('Передплату створено');
  }
  return <Layout>
    <h1>Каталог періодичних видань</h1>
    {message && <p className="message">{message}</p>}
    {session?.user.role === 'admin' && <form className="inline-form" onSubmit={createPublication}>
      <input placeholder="Назва" value={form.title} onChange={(event) => setForm({ ...form, title: event.target.value })} />
      <input placeholder="Видавець" value={form.publisher} onChange={(event) => setForm({ ...form, publisher: event.target.value })} />
      <input type="number" min="1" value={form.period_months} onChange={(event) => setForm({ ...form, period_months: Number(event.target.value) })} />
      <input value={form.price} onChange={(event) => setForm({ ...form, price: event.target.value })} />
      <button>Додати</button>
    </form>}
    <table><thead><tr><th>Назва</th><th>Видавець</th><th>Ціна</th><th></th></tr></thead><tbody>
      {publications.map((publication) => <tr key={publication.id}>
        <td>{publication.title}</td><td>{publication.publisher}</td><td>{publication.price}</td>
        <td>{session?.user.role === 'admin'
          ? <button onClick={() => api.deletePublication(publication.id).then(refresh)}>Видалити</button>
          : <button onClick={() => subscribe(publication.id)}>Передплатити</button>}</td>
      </tr>)}
    </tbody></table>
  </Layout>;
}

function SubscriptionsPage() {
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([]);
  const [payments, setPayments] = useState<Record<number, Payment[]>>({});
  const refresh = () => api.subscriptions().then(setSubscriptions);
  useEffect(() => {
    refresh();
  }, []);
  async function loadPayments(id: number) {
    setPayments({ ...payments, [id]: await api.payments(id) });
  }
  async function pay(subscription: Subscription) {
    await api.createPayment(subscription.id, subscription.total_amount);
    await loadPayments(subscription.id);
  }
  return <Layout>
    <h1>Передплати та платежі</h1>
    {subscriptions.map((subscription) => <section className="card" key={subscription.id}>
      <h2>{subscription.publication.title}</h2>
      <p>{subscription.months} міс. · {subscription.total_amount} грн · {subscription.status}</p>
      <button onClick={() => api.updateSubscription(subscription.id, subscription.months + 1).then(refresh)}>+1 місяць</button>
      <button onClick={() => api.deleteSubscription(subscription.id).then(refresh)}>Видалити</button>
      <button onClick={() => pay(subscription)}>Зареєструвати платіж</button>
      <button onClick={() => loadPayments(subscription.id)}>Показати платежі</button>
      {(payments[subscription.id] ?? []).map((payment) => <p key={payment.id}>Платіж #{payment.id}: {payment.amount}, {payment.status}</p>)}
    </section>)}
  </Layout>;
}

export default function App() {
  return <Routes>
    <Route path="/login" element={<LoginPage />} />
    <Route path="/publications" element={<ProtectedRoute><PublicationsPage /></ProtectedRoute>} />
    <Route path="/subscriptions" element={<ProtectedRoute><SubscriptionsPage /></ProtectedRoute>} />
    <Route path="*" element={<Navigate to="/publications" replace />} />
  </Routes>;
}
