import { useState } from 'react';
import { ArrowRight, BarChart3, Boxes, ShieldCheck } from 'lucide-react';
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
        <div className="hero-brand">
          <img src="/brand/stockroom-logo-text.png" alt="Stockroom" />
          <span>Inventory control for operators</span>
        </div>
        <h1>Inventory operations, sharpened for daily control.</h1>
        <p>Track stock, customers, and orders from a focused workspace built for high-trust small-business operations.</p>
        <div className="auth-proof">
          <span><ShieldCheck size={16} /> Secure access</span>
          <span><Boxes size={16} /> Live stock health</span>
          <span><BarChart3 size={16} /> Clear reporting</span>
        </div>
      </section>
      <section className="auth-card">
        <div className="auth-card-header">
          <img src="/brand/stockroom-mark.png" alt="" />
          <div>
            <h2>{mode === 'login' ? 'Welcome back' : 'Create workspace'}</h2>
            <p>{mode === 'login' ? 'Sign in to continue managing operations.' : 'Start with a clean operating system for inventory.'}</p>
          </div>
        </div>
        <div className="segmented">
          <button className={mode === 'login' ? 'selected' : ''} onClick={() => setMode('login')}>Login</button>
          <button className={mode === 'register' ? 'selected' : ''} onClick={() => setMode('register')}>Register</button>
        </div>
        <form onSubmit={submit}>
          {mode === 'register' && <label>Name<input required minLength="2" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></label>}
          <label>Email<input required type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></label>
          <label>Password<input required minLength="8" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} /></label>
          <button className="primary full" disabled={loading}>{loading ? <span className="button-loader" /> : mode === 'login' ? 'Log in' : 'Create account'} {!loading && <ArrowRight size={16} />}</button>
        </form>
      </section>
    </main>
  );
}
