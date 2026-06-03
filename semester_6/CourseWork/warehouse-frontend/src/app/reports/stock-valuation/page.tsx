"use client";

import { useEffect, useState } from "react";

import { getStockValuation, StockValuationItem } from "@/lib/api";

export default function StockValuationReportPage() {
  const [items, setItems] = useState<StockValuationItem[]>([]);
  const [total, setTotal] = useState("0");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const timer = setTimeout(() => {
      void getStockValuation()
        .then((response) => {
          setItems(response.items);
          setTotal(response.totalValuation);
        })
        .catch((loadError) => setError(loadError instanceof Error ? loadError.message : "Failed to load stock valuation."))
        .finally(() => setIsLoading(false));
    }, 0);

    return () => clearTimeout(timer);
  }, []);

  if (isLoading) return <main className="page-container">Loading stock valuation...</main>;
  if (error) return <main className="page-container">Error: {error}</main>;

  const topValuation = Math.max(...items.map((item) => Number(item.valuation)), 1);

  return (
    <main className="page-container">
      <section className="hero-card">
        <div><div className="eyebrow">Report</div><h1 className="hero-title">Stock valuation</h1><p className="hero-description">Current inventory quantities, unit costs, and total value.</p></div>
        <span className="badge">Total: {total}</span>
      </section>
      <section className="content-grid">
        <article className="panel">
          <div className="panel-header"><h2 className="section-title">Valuation bars</h2></div>
          <div className="chart-bar-list">
            {items.map((item) => (
              <div className="chart-bar-row" key={item.productId}>
                <div className="chart-bar-meta"><span>{item.sku} · {item.name}</span><span>{item.valuation}</span></div>
                <div className="chart-bar-track"><div className="chart-bar-fill" style={{ width: `${Math.max(4, (Number(item.valuation) / topValuation) * 100)}%` }} /></div>
              </div>
            ))}
          </div>
        </article>
        <article className="panel">
          <div className="panel-header"><h2 className="section-title">Summary</h2></div>
          <p className="muted-text">Products in report: {items.length}</p>
          <p className="muted-text">Total valuation: {total}</p>
        </article>
      </section>
      <section className="panel dashboard-lower-grid stock-table-panel">
        <div className="panel-header"><h2 className="section-title">Details</h2></div>
        <table className="table"><thead><tr><th>SKU</th><th>Name</th><th>Type</th><th>Quantity</th><th>Unit Cost</th><th>Valuation</th></tr></thead><tbody>
          {items.map((item) => <tr key={item.productId}><td>{item.sku}</td><td>{item.name}</td><td>{item.type}</td><td>{item.quantity}</td><td>{item.unitCost}</td><td>{item.valuation}</td></tr>)}
          {items.length === 0 ? <tr><td className="empty-cell" colSpan={6}>No stock valuation records.</td></tr> : null}
        </tbody></table>
      </section>
    </main>
  );
}
