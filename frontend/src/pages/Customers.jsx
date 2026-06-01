import { useEffect, useState } from 'react';
import { Plus, Trash2 } from 'lucide-react';
import { DataTable } from '../components/DataTable.jsx';
import { Modal } from '../components/Modal.jsx';
import { PageHeader } from '../components/PageHeader.jsx';
import { useToast } from '../components/Toast.jsx';
import { api, qs } from '../services/api.js';

export function Customers() {
  const [state, setState] = useState({ items: [], total: 0 });
  const [loading, setLoading] = useState(true);
  const [modal, setModal] = useState(false);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [sort, setSort] = useState('created_at');
  const [direction, setDirection] = useState('desc');
  const toast = useToast();
  const load = async () => {
    setLoading(true);
    try { setState(await api(`/api/customers?${qs({ search, page, sort, direction })}`)); }
    catch (err) { toast.error(err.message); }
    finally { setLoading(false); }
  };
  useEffect(() => { load(); }, [search, page, sort, direction]);
  function changeSort(key) { setDirection(sort === key && direction === 'asc' ? 'desc' : 'asc'); setSort(key); }
  async function remove(row) {
    if (!confirm(`Delete ${row.name}?`)) return;
    await api(`/api/customers/${row.id}`, { method: 'DELETE' });
    toast.success('Customer deleted');
    load();
  }
  const columns = [
    { key: 'name', label: 'Customer', sortable: true, render: (row) => <div><strong>{row.name}</strong><small>{row.company || 'Independent'}</small></div> },
    { key: 'email', label: 'Email', sortable: true },
    { key: 'phone', label: 'Phone', render: (row) => row.phone || '-' },
    { key: 'actions', label: '', render: (row) => <button className="icon-button" onClick={() => remove(row)} title="Delete"><Trash2 size={16} /></button> },
  ];
  return <>
    <PageHeader eyebrow="Relationships" title="Customers" subtitle="Keep buyer contact records ready for fast order entry." action={<button className="primary" onClick={() => setModal(true)}><Plus size={16} /> New customer</button>} />
    <DataTable columns={columns} rows={state.items} total={state.total} loading={loading} empty="No customers found." sort={sort} direction={direction} onSort={changeSort} search={search} setSearch={setSearch} page={page} setPage={setPage} />
    {modal && <CustomerModal onClose={() => setModal(false)} onDone={() => { setModal(false); load(); }} />}
  </>;
}

function CustomerModal({ onClose, onDone }) {
  const [form, setForm] = useState({ name: '', email: '', company: '', phone: '' });
  const [saving, setSaving] = useState(false);
  const toast = useToast();
  async function submit(e) {
    e.preventDefault(); setSaving(true);
    try { await api('/api/customers', { method: 'POST', body: JSON.stringify(form) }); toast.success('Customer created'); onDone(); }
    catch (err) { toast.error(err.message); }
    finally { setSaving(false); }
  }
  return <Modal title="New customer" onClose={onClose}><form className="stack" onSubmit={submit}>
    <label>Name<input required minLength="2" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></label>
    <label>Email<input required type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></label>
    <label>Company<input value={form.company} onChange={(e) => setForm({ ...form, company: e.target.value })} /></label>
    <label>Phone<input value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} /></label>
    <button className="primary full" disabled={saving}>{saving ? 'Saving...' : 'Create customer'}</button>
  </form></Modal>;
}
