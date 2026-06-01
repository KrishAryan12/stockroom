import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { api } from '../../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const raw = localStorage.getItem('stockroom.user');
    return raw ? JSON.parse(raw) : null;
  });
  const [booting, setBooting] = useState(true);

  useEffect(() => {
    if (!localStorage.getItem('stockroom.token')) {
      setBooting(false);
      return;
    }
    api('/api/auth/me')
      .then(setUser)
      .catch(() => logout())
      .finally(() => setBooting(false));
  }, []);

  function persist(token, nextUser) {
    localStorage.setItem('stockroom.token', token);
    localStorage.setItem('stockroom.user', JSON.stringify(nextUser));
    setUser(nextUser);
  }

  async function login(email, password) {
    const data = await api('/api/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) });
    persist(data.access_token, data.user);
  }

  async function register(payload) {
    const data = await api('/api/auth/register', { method: 'POST', body: JSON.stringify(payload) });
    persist(data.access_token, data.user);
  }

  function logout() {
    localStorage.removeItem('stockroom.token');
    localStorage.removeItem('stockroom.user');
    setUser(null);
  }

  const value = useMemo(() => ({ user, booting, login, register, logout, isAuthed: Boolean(user) }), [user, booting]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
