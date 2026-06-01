import { AlertTriangle, Boxes, HeartPulse, ReceiptText, TrendingUp, Users } from 'lucide-react';
import { PageHeader } from '../components/PageHeader.jsx';
import { useResource } from '../hooks/useResource.js';
import { api } from '../services/api.js';
import { date, money } from '../lib/format.js';

export function Dashboard() {
  const { data, loading, error } = useResource(() => api('/api/dashboard'), []);
  const metrics = [
    { label: 'Inventory health', value: loading ? null : `${Math.max(0, Number(data?.total_products || 0) - Number(data?.stock_alerts?.length || 0))}/${Number(data?.total_products || 0)}`, detail: 'SKUs above alert threshold', icon: HeartPulse, tone: 'good' },
    { label: 'Orders', value: data?.total_orders, detail: 'Total transactions', icon: ReceiptText },
    { label: 'Customers', value: data?.total_customers, detail: 'Active buyer records', icon: Users },
    { label: 'Revenue', value: money(data?.revenue), detail: 'Gross order value', icon: TrendingUp },
    { label: 'Inventory value', value: money(data?.inventory_value), detail: 'Current stock on hand', icon: Boxes },
  ];
  return (
    <>
      <PageHeader eyebrow="Operations" title="Command center" subtitle="A live read on inventory health, demand, and fulfillment risk." />
      {error && <div className="error-state">{error.message}</div>}
      <section className="metrics">
        {metrics.map((metric) => {
          const Icon = metric.icon;
          return <article className={`metric ${metric.tone || ''}`} key={metric.label}><div><Icon size={18} /><span>{metric.label}</span></div><strong>{loading ? <i className="skeleton short" /> : metric.value}</strong><small>{metric.detail}</small></article>;
        })}
      </section>
      <section className="dashboard-grid">
        <div className="panel panel-large">
          <header><div><h2>Recent orders</h2><small>Latest fulfillment activity</small></div></header>
          {loading ? <SkeletonList /> : data?.recent_orders?.length ? data.recent_orders.map((order) => (
            <div className="list-row" key={order.id}>
              <div><strong>{order.order_number}</strong><small>{order.customer?.name} - {date(order.created_at)}</small></div>
              <span>{money(order.total_amount)}</span>
            </div>
          )) : <div className="empty-state small"><img src="/brand/stockroom-mark.png" alt="" /><strong>Orders will appear here once created.</strong></div>}
        </div>
        <div className="panel">
          <header><div><h2>Stock alerts</h2><small>SKUs needing attention</small></div><AlertTriangle size={17} /></header>
          {loading ? <SkeletonList /> : data?.stock_alerts?.length ? data.stock_alerts.map((product) => (
            <div className="list-row alert" key={product.id}>
              <div><strong>{product.name}</strong><small>{product.sku}</small></div>
              <span>{product.quantity} left</span>
            </div>
          )) : <div className="empty-state small"><img src="/brand/stockroom-mark.png" alt="" /><strong>No products are below their threshold.</strong></div>}
        </div>
      </section>
    </>
  );
}

function SkeletonList() {
  return Array.from({ length: 4 }).map((_, index) => <div className="list-row" key={index}><span className="skeleton" /><span className="skeleton short" /></div>);
}
