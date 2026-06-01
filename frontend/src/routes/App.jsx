import { useState } from 'react';
import { useAuth } from '../features/auth/AuthContext.jsx';
import { Shell } from '../layouts/Shell.jsx';
import { AuthPage } from '../pages/AuthPage.jsx';
import { Dashboard } from '../pages/Dashboard.jsx';
import { Products } from '../pages/Products.jsx';
import { Customers } from '../pages/Customers.jsx';
import { Orders } from '../pages/Orders.jsx';

export function App() {
  const { booting, isAuthed } = useAuth();
  const [route, setRoute] = useState('dashboard');
  if (booting) return <div className="boot"><img src="/brand/stockroom-mark.png" alt="Stockroom" /><span /></div>;
  if (!isAuthed) return <AuthPage />;
  const pages = { dashboard: <Dashboard />, products: <Products />, customers: <Customers />, orders: <Orders /> };
  return <Shell route={route} setRoute={setRoute}>{pages[route]}</Shell>;
}
