"use client";

import { useEffect, useState } from "react";

import { getProductionCosts, ProductionCostItem } from "@/lib/api";

export default function ProductionCostReportPage() {
  const [items, setItems] = useState<ProductionCostItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const timer = setTimeout(() => {
      void getProductionCosts()
        .then((response) => setItems(response.items))
        .catch((loadError) => setError(loadError instanceof Error ? loadError.message : "Failed to load production cost report."))
        .finally(() => setIsLoading(false));
    }, 0);

    return () => clearTimeout(timer);
  }, []);

  if (isLoading) return <main className="page-container">Loading production costs...</main>;
  if (error) return <main className="page-container">Error: {error}</main>;

  return (
    <main className="page-container">
      <section className="hero-card"><div><div className="eyebrow">Report</div><h1 className="hero-title">Production cost</h1><p className="hero-description">Cost snapshots captured when finished goods are produced.</p></div><span className="badge">{items.length} snapshots</span></section>
      <section className="panel stock-table-panel">
        <div className="panel-header"><h2 className="section-title">Cost snapshots</h2></div>
        <table className="table"><thead><tr><th>Order</th><th>Product</th><th>Output</th><th>Total Cost</th><th>Unit Cost</th><th>Created</th></tr></thead><tbody>
          {items.map((item) => <tr key={item.snapshotId}><td>{item.productionOrderId}</td><td>{item.finishedProduct.sku} · {item.finishedProduct.name}</td><td>{item.outputQuantity}</td><td>{item.totalCost}</td><td>{item.unitCost}</td><td>{new Date(item.createdAt).toLocaleString()}</td></tr>)}
          {items.length === 0 ? <tr><td className="empty-cell" colSpan={6}>No production cost records.</td></tr> : null}
        </tbody></table>
      </section>
    </main>
  );
}
