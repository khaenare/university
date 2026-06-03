"use client";

import { useEffect, useMemo, useState } from "react";

import { getStockValuation, StockValuationItem } from "@/lib/api";

type TypeFilter = "ALL" | "COMPONENT" | "FINISHED";
type AvailabilityFilter = "ALL" | "IN_STOCK" | "EMPTY" | "LOW_STOCK";
type SortKey = "sku" | "name" | "quantity" | "unitCost" | "valuation";

function numeric(value: string): number {
  return Number(value) || 0;
}

export default function StockPage() {
  const [items, setItems] = useState<StockValuationItem[]>([]);
  const [total, setTotal] = useState("0");
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState<TypeFilter>("ALL");
  const [availabilityFilter, setAvailabilityFilter] = useState<AvailabilityFilter>("ALL");
  const [sortKey, setSortKey] = useState<SortKey>("valuation");
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("desc");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const timer = setTimeout(() => {
      void getStockValuation()
        .then((response) => {
          setItems(response.items);
          setTotal(response.totalValuation);
        })
        .catch((loadError) => {
          setError(loadError instanceof Error ? loadError.message : "Failed to load stock balance.");
        })
        .finally(() => setIsLoading(false));
    }, 0);

    return () => clearTimeout(timer);
  }, []);

  const filteredItems = useMemo(() => {
    const searchValue = search.trim().toLowerCase();

    return [...items]
      .filter((item) => {
        const matchesSearch = !searchValue || `${item.sku} ${item.name}`.toLowerCase().includes(searchValue);
        const matchesType = typeFilter === "ALL" || item.type === typeFilter;
        const quantity = numeric(item.quantity);
        const matchesAvailability =
          availabilityFilter === "ALL" ||
          (availabilityFilter === "IN_STOCK" && quantity > 0) ||
          (availabilityFilter === "EMPTY" && quantity === 0) ||
          (availabilityFilter === "LOW_STOCK" && quantity > 0 && quantity <= 5);

        return matchesSearch && matchesType && matchesAvailability;
      })
      .sort((a, b) => {
        const direction = sortDirection === "asc" ? 1 : -1;
        const left = sortKey === "sku" || sortKey === "name" ? a[sortKey] : numeric(a[sortKey]);
        const right = sortKey === "sku" || sortKey === "name" ? b[sortKey] : numeric(b[sortKey]);

        if (typeof left === "string" && typeof right === "string") {
          return left.localeCompare(right) * direction;
        }

        return ((left as number) - (right as number)) * direction;
      });
  }, [availabilityFilter, items, search, sortDirection, sortKey, typeFilter]);

  if (isLoading) {
    return <main className="page-container">Loading stock balance...</main>;
  }

  if (error) {
    return <main className="page-container">Error: {error}</main>;
  }

  return (
    <main className="page-container">
      <section className="hero-card">
        <div>
          <div className="eyebrow">Stock</div>
          <h1 className="hero-title">Stock balance</h1>
          <p className="hero-description">Search, filter, and sort current warehouse quantities and valuation.</p>
        </div>
        <span className="badge">Total value: {total}</span>
      </section>

      <section className="panel stock-controls">
        <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search SKU or name" />
        <select value={typeFilter} onChange={(event) => setTypeFilter(event.target.value as TypeFilter)}>
          <option value="ALL">All types</option>
          <option value="COMPONENT">Components</option>
          <option value="FINISHED">Finished products</option>
        </select>
        <select value={availabilityFilter} onChange={(event) => setAvailabilityFilter(event.target.value as AvailabilityFilter)}>
          <option value="ALL">All availability</option>
          <option value="IN_STOCK">In stock</option>
          <option value="LOW_STOCK">Low stock</option>
          <option value="EMPTY">Empty</option>
        </select>
        <select value={sortKey} onChange={(event) => setSortKey(event.target.value as SortKey)}>
          <option value="valuation">Sort by valuation</option>
          <option value="quantity">Sort by quantity</option>
          <option value="unitCost">Sort by unit cost</option>
          <option value="sku">Sort by SKU</option>
          <option value="name">Sort by name</option>
        </select>
        <button className="secondary-button" type="button" onClick={() => setSortDirection((current) => current === "asc" ? "desc" : "asc")}>
          {sortDirection === "asc" ? "Ascending" : "Descending"}
        </button>
      </section>

      <section className="panel stock-table-panel">
        <div className="panel-header">
          <h2 className="section-title">Balance positions</h2>
          <span className="badge">{filteredItems.length} shown</span>
        </div>
        <table className="table">
          <thead>
            <tr><th>SKU</th><th>Product</th><th>Type</th><th>Quantity</th><th>Unit</th><th>Unit Cost</th><th>Valuation</th></tr>
          </thead>
          <tbody>
            {filteredItems.map((item) => (
              <tr key={item.productId}>
                <td>{item.sku}</td>
                <td>{item.name}</td>
                <td><span className="badge">{item.type}</span></td>
                <td>{item.quantity}</td>
                <td>{item.unit}</td>
                <td>{item.unitCost}</td>
                <td>{item.valuation}</td>
              </tr>
            ))}
            {filteredItems.length === 0 ? <tr><td className="empty-cell" colSpan={7}>No matching stock positions.</td></tr> : null}
          </tbody>
        </table>
      </section>
    </main>
  );
}
