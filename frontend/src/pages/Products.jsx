import { useEffect, useState } from 'react';
import { Pencil, Plus, Trash2 } from 'lucide-react';
import { DataTable } from '../components/DataTable.jsx';
import { Modal } from '../components/Modal.jsx';
import { PageHeader } from '../components/PageHeader.jsx';
import { useToast } from '../components/Toast.jsx';
import { money } from '../lib/format.js';
import { api, qs } from '../services/api.js';

export function Products() {
  const [state, setState] = useState({ items: [], total: 0 });
  const [loading, setLoading] = useState(true);
  const [modal, setModal] = useState(false);
  const [editing, setEditing] = useState(null);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [sort, setSort] = useState('created_at');
  const [direction, setDirection] = useState('desc');
  const toast = useToast();
  const load = async () => {
    setLoading(true);
    try { setState(await api(`/api/products?${qs({ search, page, sort, direction })}`)); }
    catch (err) { toast.error(err.message); }
    finally { setLoading(false); }
  };
  useEffect(() => { load(); }, [search, page, sort, direction]);
  function changeSort(key) { setDirection(sort === key && direction === 'asc' ? 'desc' : 'asc'); setSort(key); }
  async function remove(row) {
    if (!confirm(`Delete ${row.name}?`)) return;
    await api(`/api/products/${row.id}`, { method: 'DELETE' });
    toast.success('Product deleted');
    load();
  }
  const columns = [
    { key: 'name', label: 'Product', sortable: true, render: (row) => <div><strong>{row.name}</strong><small>{row.sku}</small></div> },
    { key: 'quantity', label: 'Stock', sortable: true, render: (row) => <span className={row.quantity <= row.low_stock_threshold ? 'badge danger' : 'badge'}>{row.quantity}</span> },
    { key: 'unit_price', label: 'Price', sortable: true, render: (row) => money(row.unit_price) },
    { key: 'actions', label: '', render: (row) => <div className="row-actions"><button className="icon-button" onClick={() => setEditing(row)} title="Edit product"><Pencil size={16} /></button><button className="icon-button danger" onClick={() => remove(row)} title="Delete product"><Trash2 size={16} /></button></div> },
  ];
  return <>
    <PageHeader eyebrow="Catalog" title="Products" subtitle="Maintain SKUs, pricing, and live stock thresholds." action={<button className="primary" onClick={() => setModal(true)}><Plus size={16} /> New product</button>} />
    <DataTable columns={columns} rows={state.items} total={state.total} loading={loading} empty="No products found." sort={sort} direction={direction} onSort={changeSort} search={search} setSearch={setSearch} page={page} setPage={setPage} />
    {modal && <ProductModal onClose={() => setModal(false)} onDone={() => { setModal(false); load(); }} />}
    {editing && <ProductModal product={editing} onClose={() => setEditing(null)} onDone={() => { setEditing(null); load(); }} />}
  </>;
}

function ProductModal({ product, onClose, onDone }) {
  const [form, setForm] = useState(product ? {
    name: product.name,
    sku: product.sku,
    description: product.description || '',
    unit_price: product.unit_price,
    quantity: product.quantity,
    low_stock_threshold: product.low_stock_threshold,
  } : { name: '', sku: '', description: '', unit_price: '', quantity: 0, low_stock_threshold: 5 });
  const [saving, setSaving] = useState(false);
  const toast = useToast();
  async function submit(e) {
    e.preventDefault(); setSaving(true);
    try {
      await api(product ? `/api/products/${product.id}` : '/api/products', { method: product ? 'PUT' : 'POST', body: JSON.stringify(form) });
      toast.success(product ? 'Product updated' : 'Product created');
      onDone();
    }
    catch (err) { toast.error(err.message); }
    finally { setSaving(false); }
  }
  return <Modal title={product ? 'Edit product' : 'New product'} onClose={onClose}><form className="stack" onSubmit={submit}>
    <label>Name<input required minLength="2" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></label>
    <label>SKU<input required value={form.sku} onChange={(e) => setForm({ ...form, sku: e.target.value })} /></label>
    <label>Description<textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></label>
    <div className="form-grid"><label>Price<input required min="0.01" step="0.01" type="number" value={form.unit_price} onChange={(e) => setForm({ ...form, unit_price: e.target.value })} /></label><label>Quantity<input required min="0" type="number" value={form.quantity} onChange={(e) => setForm({ ...form, quantity: Number(e.target.value) })} /></label></div>
    <label>Low stock threshold<input required min="0" type="number" value={form.low_stock_threshold} onChange={(e) => setForm({ ...form, low_stock_threshold: Number(e.target.value) })} /></label>
    <button className="primary full" disabled={saving}>{saving ? 'Saving...' : product ? 'Save product' : 'Create product'}</button>
  </form></Modal>;
}
