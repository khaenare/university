"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import {
  getMovements,
  getProductionCosts,
  getStockValuation,
  MovementItem,
  ProductionCostItem,
  StockValuationItem,
} from "@/lib/api";

function money(value: string | number): string {
  return Number(value).toLocaleString("en-US", {
    maximumFractionDigits: 2,
    minimumFractionDigits: 2,
  });
}

function formatDate(value: string): string {
  return new Date(value).toLocaleString("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export default function Home() {
  const [stockItems, setStockItems] = useState<StockValuationItem[]>([]);
  const [stockTotal, setStockTotal] = useState("0");
  const [movementItems, setMovementItems] = useState<MovementItem[]>([]);
  const [productionItems, setProductionItems] = useState<ProductionCostItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const timer = setTimeout(() => {
      async function loadDashboard() {
        try {
          setIsLoading(true);
          setError(null);

          const [stock, movements, production] = await Promise.all([
            getStockValuation(),
            getMovements(6),
            getProductionCosts(4),
          ]);

          setStockItems(stock.items);
          setStockTotal(stock.totalValuation);
          setMovementItems(movements.items);
          setProductionItems(production.items);
        } catch (loadError) {
          setError(loadError instanceof Error ? loadError.message : "Failed to load dashboard.");
        } finally {
          setIsLoading(false);
        }
      }

      void loadDashboard();
    }, 0);

    return () => {
      clearTimeout(timer);
    };
  }, []);

  if (isLoading) {
    return <main className="page-container">Loading dashboard...</main>;
  }

  if (error) {
    return <main className="page-container">Error: {error}</main>;
  }

  const productsInStock = stockItems.filter((item) => Number(item.quantity) > 0).length;
  const lowStockItems = stockItems.filter((item) => Number(item.quantity) > 0 && Number(item.quantity) <= 5);
  const topValuation = Math.max(...stockItems.map((item) => Number(item.valuation)), 1);
  const topProducts = [...stockItems]
    .sort((a, b) => Number(b.valuation) - Number(a.valuation))
    .slice(0, 5);

  return (
    <main className="page-container">
      <section className="hero-card">
        <div>
          <div className="eyebrow">Dashboard</div>
          <h2 className="hero-title">Warehouse control center</h2>
          <p className="hero-description">
            Live overview of inventory value, stock risks, recent movements, and production cost snapshots.
          </p>
        </div>
        <div className="hero-actions">
          <Link className="secondary-button action-link" href="/reports">Open Reports</Link>
          <Link className="secondary-button action-link" href="/receipts">Create Receipt</Link>
        </div>
      </section>

      <section className="stats-grid">
        <article className="stat-card">
          <div className="stat-label">Stock valuation</div>
          <div className="stat-value">${money(stockTotal)}</div>
        </article>
        <article className="stat-card">
          <div className="stat-label">Products in stock</div>
          <div className="stat-value">{productsInStock}</div>
        </article>
        <article className="stat-card">
          <div className="stat-label">Low stock items</div>
          <div className="stat-value">{lowStockItems.length}</div>
        </article>
      </section>

      <section className="content-grid">
        <article className="panel">
          <div className="panel-header">
            <h2 className="section-title">Top stock value</h2>
            <Link href="/reports">Details</Link>
          </div>
          <div className="chart-bar-list">
            {topProducts.map((item) => {
              const width = `${Math.max((Number(item.valuation) / topValuation) * 100, 4)}%`;

              return (
                <div className="chart-bar-row" key={item.productId}>
                  <div className="chart-bar-meta">
                    <span>{item.sku} · {item.name}</span>
                    <span>${money(item.valuation)}</span>
                  </div>
                  <div className="chart-bar-track">
                    <div className="chart-bar-fill" style={{ width }} />
                  </div>
                </div>
              );
            })}
            {topProducts.length === 0 ? <p className="muted-text">No stock valuation data yet.</p> : null}
          </div>
        </article>

        <article className="panel">
          <div className="panel-header">
            <h2 className="section-title">Low stock watch</h2>
          </div>
          <div className="line-list">
            {lowStockItems.slice(0, 5).map((item) => (
              <div className="activity-row" key={item.productId}>
                <strong>{item.sku}</strong>
                <span>{item.quantity} {item.unit} available</span>
              </div>
            ))}
            {lowStockItems.length === 0 ? <p className="muted-text">No low-stock risks in current demo data.</p> : null}
          </div>
        </article>
      </section>

      <section className="content-grid dashboard-lower-grid">
        <article className="panel">
          <div className="panel-header">
            <h2 className="section-title">Recent movements</h2>
            <Link href="/reports">All movements</Link>
          </div>
          <table className="table">
            <thead>
              <tr><th>Product</th><th>Type</th><th>Quantity</th><th>Time</th></tr>
            </thead>
            <tbody>
              {movementItems.map((item) => (
                <tr key={item.id}>
                  <td>{item.product.sku} · {item.product.name}</td>
                  <td><span className="badge">{item.type}</span></td>
                  <td>{item.quantity} {item.product.unit}</td>
                  <td>{formatDate(item.createdAt)}</td>
                </tr>
              ))}
              {movementItems.length === 0 ? <tr><td className="empty-cell" colSpan={4}>No movements yet.</td></tr> : null}
            </tbody>
          </table>
        </article>

        <article className="panel">
          <div className="panel-header">
            <h2 className="section-title">Latest production costs</h2>
            <Link href="/production-orders">New order</Link>
          </div>
          <div className="line-list">
            {productionItems.map((item) => (
              <div className="activity-row" key={item.snapshotId}>
                <strong>{item.finishedProduct.sku} · {item.finishedProduct.name}</strong>
                <span>${money(item.unitCost)} per {item.finishedProduct.unit}</span>
              </div>
            ))}
            {productionItems.length === 0 ? <p className="muted-text">No production cost snapshots yet.</p> : null}
          </div>
        </article>
      </section>
    </main>
  );
}
