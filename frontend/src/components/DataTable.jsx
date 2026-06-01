import { ChevronDown, ChevronUp, Search } from 'lucide-react';

export function DataTable({ columns, rows, loading, empty, sort, direction, onSort, search, setSearch, page, setPage, total, pageSize = 10 }) {
  const pages = Math.max(1, Math.ceil((total || 0) / pageSize));
  return (
    <section className="table-wrap">
      <div className="table-toolbar">
        <div className="searchbox">
          <Search size={16} />
          <input value={search} onChange={(event) => { setPage(1); setSearch(event.target.value); }} placeholder="Search" />
        </div>
      </div>
      <div className="table-scroll">
        <table>
          <thead>
            <tr>
              {columns.map((column) => (
                <th key={column.key}>
                  {column.sortable ? (
                    <button onClick={() => onSort(column.key)}>
                      {column.label}
                      {sort === column.key && (direction === 'asc' ? <ChevronUp size={14} /> : <ChevronDown size={14} />)}
                    </button>
                  ) : column.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading && Array.from({ length: 5 }).map((_, index) => (
              <tr key={index}>{columns.map((column) => <td key={column.key}><span className="skeleton" /></td>)}</tr>
            ))}
            {!loading && rows.map((row) => (
              <tr key={row.id}>{columns.map((column) => <td key={column.key}>{column.render ? column.render(row) : row[column.key]}</td>)}</tr>
            ))}
          </tbody>
        </table>
      </div>
      {!loading && rows.length === 0 && <div className="empty-state">{empty}</div>}
      <footer className="pagination">
        <span>{total || 0} records</span>
        <div>
          <button disabled={page <= 1} onClick={() => setPage(page - 1)}>Previous</button>
          <span>{page} / {pages}</span>
          <button disabled={page >= pages} onClick={() => setPage(page + 1)}>Next</button>
        </div>
      </footer>
    </section>
  );
}
