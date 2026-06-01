import { AlertTriangle, Boxes, ReceiptText, TrendingUp, Users } from 'lucide-react';
import { PageHeader } from '../components/PageHeader.jsx';
import { useResource } from '../hooks/useResource.js';
import { api } from '../services/api.js';
import { date, money } from '../lib/format.js';

export function Dashboard() {
  const { data, loading, error } = useResource(() => api('/api/dashboard'), []);
  const metrics = [
    { label: 'Products', value: data?.total_products, icon: Boxes },
    { label: 'Customers', value: data?.total_customers, icon: Users },
    { label: 'Orders', value: data?.total_orders, icon: ReceiptText },
    { label: 'Inventory value', value: money(data?.inventory_value), icon: TrendingUp },
  ];
  return (
    <>
      <PageHeader eyebrow="Operations" title="Dashboard" subtitle="A live read on catalog health, demand, and inventory risk." />
      {error && <div className="error-state">{error.message}</div>}
      <section className="metrics">
        {metrics.map((metric) => {
          const Icon = metric.icon;
          return <article className="metric" key={metric.label}><Icon size={18} /><span>{metric.label}</span><strong>{loading ? <i className="skeleton short" /> : metric.value}</strong></article>;
        })}
      </section>
      <section className="dashboard-grid">
        <div className="panel">
          <header><h2>Recent orders</h2></header>
          {loading ? <SkeletonList /> : data?.recent_orders?.length ? data.recent_orders.map((order) => (
            <div className="list-row" key={order.id}>
              <div><strong>{order.order_number}</strong><small>{order.customer?.name} - {date(order.created_at)}</small></div>
              <span>{money(order.total_amount)}</span>
            </div>
          )) : <div className="empty-state small">Orders will appear here once created.</div>}
        </div>
        <div className="panel">
          <header><h2>Stock alerts</h2><AlertTriangle size={17} /></header>
          {loading ? <SkeletonList /> : data?.stock_alerts?.length ? data.stock_alerts.map((product) => (
            <div className="list-row alert" key={product.id}>
              <div><strong>{product.name}</strong><small>{product.sku}</small></div>
              <span>{product.quantity} left</span>
            </div>
          )) : <div className="empty-state small">No products are below their threshold.</div>}
        </div>
      </section>
    </>
  );
}

function SkeletonList() {
  return Array.from({ length: 4 }).map((_, index) => <div className="list-row" key={index}><span className="skeleton" /><span className="skeleton short" /></div>);
}
