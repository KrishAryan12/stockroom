export function Brand({ tone = 'dark', size = 'default', showTagline = false }) {
  return (
    <div className={`brand brand-${tone} brand-${size}`}>
      <img className="brand-mark" src="/brand/stockroom-mark.png" alt="" />
      <div className="brand-copy">
        <span>Stockroom</span>
        {showTagline && <small>Inventory control for operators</small>}
      </div>
    </div>
  );
}
