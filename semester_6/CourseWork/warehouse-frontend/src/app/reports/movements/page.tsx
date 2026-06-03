"use client";

import { useEffect, useMemo, useState } from "react";

import { getMovements, MovementItem } from "@/lib/api";

export default function MovementsReportPage() {
  const [items, setItems] = useState<MovementItem[]>([]);
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState("ALL");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const timer = setTimeout(() => {
      void getMovements()
        .then((response) => setItems(response.items))
        .catch((loadError) => setError(loadError instanceof Error ? loadError.message : "Failed to load movements report."))
        .finally(() => setIsLoading(false));
    }, 0);

    return () => clearTimeout(timer);
  }, []);

  const filteredItems = useMemo(() => {
    const searchValue = search.trim().toLowerCase();
    return items.filter((item) => {
      const matchesSearch = !searchValue || `${item.product.sku} ${item.product.name}`.toLowerCase().includes(searchValue);
      const matchesType = typeFilter === "ALL" || item.type === typeFilter;
      return matchesSearch && matchesType;
    });
  }, [items, search, typeFilter]);

  const movementTypes = Array.from(new Set(items.map((item) => item.type))).sort();

  if (isLoading) return <main className="page-container">Loading movements...</main>;
  if (error) return <main className="page-container">Error: {error}</main>;

  return (
    <main className="page-container">
      <section className="hero-card"><div><div className="eyebrow">Report</div><h1 className="hero-title">Inventory movements</h1><p className="hero-description">Filtered movement ledger for receipts, sales issues, and production postings.</p></div><span className="badge">{filteredItems.length} shown</span></section>
      <section className="panel stock-controls">
        <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search product" />
        <select value={typeFilter} onChange={(event) => setTypeFilter(event.target.value)}>
          <option value="ALL">All movement types</option>
          {movementTypes.map((type) => <option key={type} value={type}>{type}</option>)}
        </select>
      </section>
      <section className="panel stock-table-panel">
        <div className="panel-header"><h2 className="section-title">Movement ledger</h2></div>
        <table className="table"><thead><tr><th>Product</th><th>Type</th><th>Quantity</th><th>Unit Cost</th><th>Source</th><th>Created</th></tr></thead><tbody>
          {filteredItems.map((item) => <tr key={item.id}><td>{item.product.sku} · {item.product.name}</td><td><span className="badge">{item.type}</span></td><td>{item.quantity} {item.product.unit}</td><td>{item.unitCost ?? "-"}</td><td>{item.sourceDocument ?? "-"}</td><td>{new Date(item.createdAt).toLocaleString()}</td></tr>)}
          {filteredItems.length === 0 ? <tr><td className="empty-cell" colSpan={6}>No matching movements.</td></tr> : null}
        </tbody></table>
      </section>
    </main>
  );
}
