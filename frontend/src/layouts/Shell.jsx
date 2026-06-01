import { BarChart3, Boxes, LogOut, ReceiptText, Users } from 'lucide-react';
import { useAuth } from '../features/auth/AuthContext.jsx';
import { Brand } from '../components/Brand.jsx';

const nav = [
  { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
  { id: 'products', label: 'Products', icon: Boxes },
  { id: 'customers', label: 'Customers', icon: Users },
  { id: 'orders', label: 'Orders', icon: ReceiptText },
];

export function Shell({ route, setRoute, children }) {
  const { user, logout } = useAuth();
  return (
    <div className="shell">
      <aside className="sidebar">
        <button className="brand-button" onClick={() => setRoute('dashboard')} aria-label="Go to dashboard">
          <Brand tone="light" showTagline />
        </button>
        <nav>
          {nav.map((item) => {
            const Icon = item.icon;
            return (
              <button key={item.id} className={route === item.id ? 'active' : ''} onClick={() => setRoute(item.id)}>
                <Icon size={18} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
        <div className="user-panel">
          <div className="avatar">{user.name?.charAt(0) || 'S'}</div>
          <div>
            <strong>{user.name}</strong>
            <small>{user.email}</small>
          </div>
          <button className="icon-button" onClick={logout} title="Log out"><LogOut size={18} /></button>
        </div>
      </aside>
      <main className="main">{children}</main>
    </div>
  );
}
