import { useEffect, useMemo, useState } from 'react';
import { Eye, Plus, Trash2, X } from 'lucide-react';
import { DataTable } from '../components/DataTable.jsx';
import { Modal } from '../components/Modal.jsx';
import { PageHeader } from '../components/PageHeader.jsx';
import { useToast } from '../components/Toast.jsx';
import { date, money } from '../lib/format.js';
import { api, qs } from '../services/api.js';

export function Orders() {
  const [state, setState] = useState({ items: [], total: 0 });
  const [loading, setLoading] = useState(true);
  const [modal, setModal] = useState(false);
  const [selected, setSelected] = useState(null);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [sort, setSort] = useState('created_at');
  const [direction, setDirection] = useState('desc');
  const toast = useToast();
  const load = async () => {
    setLoading(true);
    try { setState(await api(`/api/orders?${qs({ search, page, sort, direction })}`)); }
    catch (err) { toast.error(err.message); }
    finally { setLoading(false); }
  };
  useEffect(() => { load(); }, [search, page, sort, direction]);
  function changeSort(key) { setDirection(sort === key && direction === 'asc' ? 'desc' : 'asc'); setSort(key); }
  async function remove(row) {
    if (!confirm(`Cancel ${row.order_number}? Stock will be returned.`)) return;
    await api(`/api/orders/${row.id}`, { method: 'DELETE' });
    toast.success('Order cancelled');
    load();
  }
  const columns = [
    { key: 'order_number', label: 'Order', sortable: true, render: (row) => <div><strong>{row.order_number}</strong><small>{row.customer?.name || 'Customer'}</small></div> },
    { key: 'created_at', label: 'Date', sortable: true, render: (row) => date(row.created_at) },
    { key: 'total_amount', label: 'Total', sortable: true, render: (row) => money(row.total_amount) },
    { key: 'status', label: 'Status', sortable: true, render: (row) => <span className="badge">{row.status}</span> },
    { key: 'actions', label: '', render: (row) => <div className="row-actions"><button className="icon-button" onClick={() => setSelected(row)} title="View order"><Eye size={16} /></button><button className="icon-button danger" onClick={() => remove(row)} title="Cancel order"><Trash2 size={16} /></button></div> },
  ];
  return <>
    <PageHeader eyebrow="Fulfillment" title="Orders" subtitle="Create transactions, inspect line items, and cancel safely with stock returned." action={<button className="primary" onClick={() => setModal(true)}><Plus size={16} /> New order</button>} />
    <DataTable columns={columns} rows={state.items} total={state.total} loading={loading} empty="No orders found." sort={sort} direction={direction} onSort={changeSort} search={search} setSearch={setSearch} page={page} setPage={setPage} />
    {modal && <OrderModal onClose={() => setModal(false)} onDone={() => { setModal(false); load(); }} />}
    {selected && <OrderDetails order={selected} onClose={() => setSelected(null)} />}
  </>;
}

function OrderDetails({ order, onClose }) {
  return <Modal title={order.order_number} onClose={onClose}>
    <div className="detail-summary">
      <div><span>Customer</span><strong>{order.customer?.name || 'Customer'}</strong><small>{order.customer?.email}</small></div>
      <div><span>Status</span><strong>{order.status}</strong><small>{date(order.created_at)}</small></div>
      <div><span>Total</span><strong>{money(order.total_amount)}</strong><small>{order.items.length} line items</small></div>
    </div>
    <div className="line-items">
      {order.items.map((item) => <div className="line-item" key={item.id}>
        <div><strong>{item.product?.name || `Product ${item.product_id}`}</strong><small>{item.product?.sku}</small></div>
        <span>{item.quantity} x {money(item.unit_price)}</span>
        <strong>{money(item.line_total)}</strong>
      </div>)}
    </div>
    <button className="secondary full" onClick={onClose}><X size={16} /> Close</button>
  </Modal>;
}

function OrderModal({ onClose, onDone }) {
  const [customers, setCustomers] = useState([]);
  const [products, setProducts] = useState([]);
  const [customerId, setCustomerId] = useState('');
  const [items, setItems] = useState([{ product_id: '', quantity: 1 }]);
  const [saving, setSaving] = useState(false);
  const toast = useToast();
  useEffect(() => {
    api('/api/customers?page_size=100').then((data) => setCustomers(data.items)).catch((err) => toast.error(err.message));
    api('/api/products?page_size=100').then((data) => setProducts(data.items)).catch((err) => toast.error(err.message));
  }, []);
  const total = useMemo(() => items.reduce((sum, item) => {
    const product = products.find((candidate) => candidate.id === Number(item.product_id));
    return sum + Number(product?.unit_price || 0) * Number(item.quantity || 0);
  }, 0), [items, products]);
  async function submit(e) {
    e.preventDefault(); setSaving(true);
    const payload = { customer_id: Number(customerId), items: items.map((item) => ({ product_id: Number(item.product_id), quantity: Number(item.quantity) })) };
    try {
      await api('/api/orders', { method: 'POST', headers: { 'Idempotency-Key': crypto.randomUUID() }, body: JSON.stringify(payload) });
      toast.success('Order created');
      onDone();
    } catch (err) { toast.error(err.message); }
    finally { setSaving(false); }
  }
  return <Modal title="New order" onClose={onClose}><form className="stack" onSubmit={submit}>
    <label>Customer<select required value={customerId} onChange={(e) => setCustomerId(e.target.value)}><option value="">Select customer</option>{customers.map((customer) => <option key={customer.id} value={customer.id}>{customer.name}</option>)}</select></label>
    {items.map((item, index) => <div className="form-grid" key={index}>
      <label>Product<select required value={item.product_id} onChange={(e) => setItems(items.map((row, i) => i === index ? { ...row, product_id: e.target.value } : row))}><option value="">Select product</option>{products.map((product) => <option key={product.id} value={product.id}>{product.name} ({product.quantity})</option>)}</select></label>
      <label>Qty<input min="1" required type="number" value={item.quantity} onChange={(e) => setItems(items.map((row, i) => i === index ? { ...row, quantity: e.target.value } : row))} /></label>
    </div>)}
    <button type="button" className="secondary" onClick={() => setItems([...items, { product_id: '', quantity: 1 }])}>Add line</button>
    <div className="order-total"><span>Estimated total</span><strong>{money(total)}</strong></div>
    <button className="primary full" disabled={saving}>{saving ? 'Creating...' : 'Create order'}</button>
  </form></Modal>;
}
