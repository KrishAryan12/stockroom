import { useState } from 'react';
import { ArrowRight } from 'lucide-react';
import { useAuth } from '../features/auth/AuthContext.jsx';
import { useToast } from '../components/Toast.jsx';

export function AuthPage() {
  const [mode, setMode] = useState('login');
  const [form, setForm] = useState({ name: '', email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const auth = useAuth();
  const toast = useToast();

  async function submit(event) {
    event.preventDefault();
    setLoading(true);
    try {
      if (mode === 'login') await auth.login(form.email, form.password);
      else await auth.register(form);
      toast.success('Welcome to Stockroom');
    } catch (err) {
      toast.error(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-screen">
      <section className="auth-hero">
        <div className="brand large"><span className="brand-mark">S</span><span>Stockroom</span></div>
        <h1>Inventory operations with the edges sanded down.</h1>
        <p>Track stock, customers, and orders from a focused workspace built for daily small-business operations.</p>
      </section>
      <section className="auth-card">
        <div className="segmented">
          <button className={mode === 'login' ? 'selected' : ''} onClick={() => setMode('login')}>Login</button>
          <button className={mode === 'register' ? 'selected' : ''} onClick={() => setMode('register')}>Register</button>
        </div>
        <form onSubmit={submit}>
          {mode === 'register' && <label>Name<input required minLength="2" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></label>}
          <label>Email<input required type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></label>
          <label>Password<input required minLength="8" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} /></label>
          <button className="primary full" disabled={loading}>{loading ? 'Working...' : mode === 'login' ? 'Log in' : 'Create account'} <ArrowRight size={16} /></button>
        </form>
      </section>
    </main>
  );
}
