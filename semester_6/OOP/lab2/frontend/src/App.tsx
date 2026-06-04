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
      <Link className="brand" to="/publications">Periodicals</Link>
      <nav>
        <Link to="/publications">Каталог</Link>
        <Link to="/subscriptions">Передплати</Link>
      </nav>
      <div className="user-pill">{session?.user.username}<small>{session?.user.role}</small></div>
      <button className="ghost-button" onClick={() => { logout(); navigate('/login'); }}>Вийти</button>
    </header>
    <main className="page-shell">{children}</main>
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
  return <main className="login-page">
    <section className="login-hero">
      <span className="eyebrow">Лабораторна робота 2</span>
      <h1>Система періодичних видань</h1>
      <p>Керуйте каталогом, оформлюйте передплати та реєструйте платежі через JWT-захищений вебдодаток.</p>
    </section>
    <section className="login-card">
      <h2>Вхід</h2>
      <p className="muted">Тестові дані: reader/password або admin/password</p>
      <form onSubmit={submit}>
        <label>Логін<input value={username} onChange={(event) => setUsername(event.target.value)} /></label>
        <label>Пароль<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} /></label>
      {error && <p className="error">{error}</p>}
        <button type="submit">Увійти</button>
      </form>
    </section>
  </main>;
}

function PublicationsPage() {
  const { session } = useAuth();
  const [publications, setPublications] = useState<Publication[]>([]);
  const [form, setForm] = useState({ title: '', publisher: '', period_months: 1, price: '0.00' });
  const [editingId, setEditingId] = useState<number | null>(null);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const refresh = () => {
    setLoading(true);
    api.publications()
      .then(setPublications)
      .catch((error) => setMessage(error.message))
      .finally(() => setLoading(false));
  };
  useEffect(() => {
    refresh();
  }, []);
  async function createPublication(event: FormEvent) {
    event.preventDefault();
    try {
      if (editingId) {
        await api.updatePublication(editingId, form);
        setMessage('Видання оновлено');
      } else {
        await api.createPublication(form);
        setMessage('Видання додано до каталогу');
      }
      setForm({ title: '', publisher: '', period_months: 1, price: '0.00' });
      setEditingId(null);
      refresh();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Не вдалося зберегти видання');
    }
  }
  function startEdit(publication: Publication) {
    setEditingId(publication.id);
    setForm({
      title: publication.title,
      publisher: publication.publisher,
      period_months: publication.period_months,
      price: publication.price,
    });
    setMessage('Редагування видання');
  }
  function cancelEdit() {
    setEditingId(null);
    setForm({ title: '', publisher: '', period_months: 1, price: '0.00' });
  }
  async function subscribe(publicationId: number) {
    try {
      await api.createSubscription(publicationId, 1);
      setMessage('Передплату створено');
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Не вдалося оформити передплату');
    }
  }
  return <Layout>
    <section className="hero-card">
      <div>
        <span className="eyebrow">Каталог</span>
        <h1>Періодичні видання</h1>
        <p>Обирайте журнали та газети для передплати або керуйте каталогом як адміністратор.</p>
      </div>
      <div className="stat-card"><strong>{publications.length}</strong><span>видань</span></div>
    </section>
    {message && <p className="message">{message}</p>}
    {session?.user.role === 'admin' && <section className="panel">
      <h2>Додати видання</h2>
      <form className="inline-form" onSubmit={createPublication}>
        <input placeholder="Назва" value={form.title} onChange={(event) => setForm({ ...form, title: event.target.value })} />
        <input placeholder="Видавець" value={form.publisher} onChange={(event) => setForm({ ...form, publisher: event.target.value })} />
        <input aria-label="Період" type="number" min="1" value={form.period_months} onChange={(event) => setForm({ ...form, period_months: Number(event.target.value) })} />
        <input aria-label="Ціна" value={form.price} onChange={(event) => setForm({ ...form, price: event.target.value })} />
        <button type="submit">{editingId ? 'Зберегти' : 'Додати'}</button>
      </form>
      {editingId && <button className="secondary-button form-cancel" onClick={cancelEdit}>Скасувати редагування</button>}
    </section>}
    <section className="panel">
      {loading ? <p className="muted">Завантаження каталогу...</p> : publications.length === 0 ? <p className="muted">Каталог поки порожній.</p> :
        <div className="table-wrap"><table><thead><tr><th>Назва</th><th>Видавець</th><th>Період</th><th>Ціна</th><th></th></tr></thead><tbody>
          {publications.map((publication) => <tr key={publication.id}>
            <td><strong>{publication.title}</strong></td><td>{publication.publisher}</td><td>{publication.period_months} міс.</td><td><span className="price">{publication.price} грн</span></td>
            <td>{session?.user.role === 'admin'
              ? <div className="row-actions"><button className="secondary-button" onClick={() => startEdit(publication)}>Редагувати</button><button className="danger-button" onClick={() => api.deletePublication(publication.id).then(refresh)}>Видалити</button></div>
              : <button onClick={() => subscribe(publication.id)}>Передплатити</button>}</td>
          </tr>)}
        </tbody></table></div>}
    </section>
  </Layout>;
}

function SubscriptionsPage() {
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([]);
  const [payments, setPayments] = useState<Record<number, Payment[]>>({});
  const [monthsDraft, setMonthsDraft] = useState<Record<number, number>>({});
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const refresh = () => {
    setLoading(true);
    api.subscriptions()
      .then(setSubscriptions)
      .catch((error) => setMessage(error.message))
      .finally(() => setLoading(false));
  };
  useEffect(() => {
    refresh();
  }, []);
  async function loadPayments(id: number) {
    try {
      setPayments({ ...payments, [id]: await api.payments(id) });
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Не вдалося завантажити платежі');
    }
  }
  async function pay(subscription: Subscription) {
    try {
      await api.createPayment(subscription.id, subscription.total_amount);
      setMessage('Платіж зареєстровано');
      await loadPayments(subscription.id);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Не вдалося зареєструвати платіж');
    }
  }
  async function updateMonths(subscription: Subscription) {
    const months = monthsDraft[subscription.id] ?? subscription.months;
    try {
      await api.updateSubscription(subscription.id, months);
      setMessage('Термін передплати оновлено');
      refresh();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Не вдалося оновити передплату');
    }
  }
  async function updatePaymentStatus(payment: Payment, status: string, subscriptionId: number) {
    try {
      await api.updatePayment(payment.id, status);
      setMessage('Статус платежу оновлено');
      await loadPayments(subscriptionId);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Не вдалося оновити платіж');
    }
  }
  async function deletePayment(payment: Payment, subscriptionId: number) {
    try {
      await api.deletePayment(payment.id);
      setMessage('Платіж видалено');
      await loadPayments(subscriptionId);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Не вдалося видалити платіж');
    }
  }
  return <Layout>
    <section className="hero-card">
      <div>
        <span className="eyebrow">Особистий кабінет</span>
        <h1>Передплати та платежі</h1>
        <p>Контролюйте термін передплати, суму до оплати та історію зареєстрованих платежів.</p>
      </div>
      <div className="stat-card"><strong>{subscriptions.length}</strong><span>передплат</span></div>
    </section>
    {message && <p className="message">{message}</p>}
    {loading ? <section className="panel"><p className="muted">Завантаження передплат...</p></section> : subscriptions.length === 0 ? <section className="panel empty-state"><h2>Передплат ще немає</h2><p>Перейдіть до каталогу та оберіть періодичне видання.</p><Link className="button-link" to="/publications">До каталогу</Link></section> :
      <div className="subscription-grid">{subscriptions.map((subscription) => <section className="card" key={subscription.id}>
        <div className="card-header">
          <div><h2>{subscription.publication.title}</h2><p>{subscription.publication.publisher}</p></div>
          <span className="badge">{subscription.status}</span>
        </div>
        <div className="metrics">
          <span><strong>{subscription.months}</strong> міс.</span>
          <span><strong>{subscription.total_amount}</strong> грн</span>
        </div>
        <div className="months-editor">
          <label>Новий термін, міс.
            <input type="number" min="1" value={monthsDraft[subscription.id] ?? subscription.months} onChange={(event) => setMonthsDraft({ ...monthsDraft, [subscription.id]: Number(event.target.value) })} />
          </label>
          <button className="secondary-button" onClick={() => updateMonths(subscription)}>Оновити</button>
        </div>
        <div className="actions">
          <button className="danger-button" onClick={() => api.deleteSubscription(subscription.id).then(refresh)}>Видалити</button>
          <button onClick={() => pay(subscription)}>Платіж</button>
          <button className="secondary-button" onClick={() => loadPayments(subscription.id)}>Показати платежі</button>
        </div>
        <div className="payment-list">
          {(payments[subscription.id] ?? []).map((payment) => <div className="payment-row" key={payment.id}>
            <span>#{payment.id}</span>
            <strong>{payment.amount} грн</strong>
            <select aria-label={`Статус платежу ${payment.id}`} value={payment.status} onChange={(event) => updatePaymentStatus(payment, event.target.value, subscription.id)}>
              <option value="registered">registered</option>
              <option value="paid">paid</option>
              <option value="cancelled">cancelled</option>
            </select>
            <button className="danger-button compact-button" onClick={() => deletePayment(payment, subscription.id)}>Видалити</button>
          </div>)}
        </div>
      </section>)}</div>}
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
