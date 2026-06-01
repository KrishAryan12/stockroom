import { createContext, useContext, useMemo, useState } from 'react';
import { CheckCircle2, XCircle } from 'lucide-react';

const ToastContext = createContext(null);

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);
  function push(type, message) {
    const id = crypto.randomUUID();
    setToasts((items) => [...items, { id, type, message }]);
    setTimeout(() => setToasts((items) => items.filter((item) => item.id !== id)), 3600);
  }
  const value = useMemo(() => ({ success: (message) => push('success', message), error: (message) => push('error', message) }), []);
  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="toast-stack">
        {toasts.map((toast) => (
          <div className={`toast ${toast.type}`} key={toast.id}>
            {toast.type === 'success' ? <CheckCircle2 size={18} /> : <XCircle size={18} />}
            <span>{toast.message}</span>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  return useContext(ToastContext);
}
