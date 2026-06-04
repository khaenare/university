"use client";

import { FormEvent, useEffect, useState } from "react";

import {
  createProductionOrder,
  getProductionOrders,
  getProducts,
  ProductionOrderItem,
  ProductOption,
} from "@/lib/api";
import { buildProductionOrderPayload } from "@/lib/form-payloads";

export default function ProductionOrdersPage() {
  const [items, setItems] = useState<ProductionOrderItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [products, setProducts] = useState<ProductOption[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  async function load() {
    const [ordersResponse, productsResponse] = await Promise.all([getProductionOrders(), getProducts()]);
    setItems(ordersResponse.items);
    setProducts(productsResponse.filter((product) => product.type === "FINISHED"));
  }

  useEffect(() => {
    const timer = setTimeout(() => {
      void load().catch((loadError) => {
        setError(loadError instanceof Error ? loadError.message : "Failed to load production orders.");
      });
    }, 0);

    return () => {
      clearTimeout(timer);
    };
  }, []);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const formData = new FormData(form);

    try {
      setIsSubmitting(true);
      setError(null);
      setSuccessMessage(null);
      await createProductionOrder(buildProductionOrderPayload(formData));

      form.reset();
      await load();
      setSuccessMessage("Production order created successfully.");
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Failed to create production order.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="page-container">
      <section className="hero-card">
        <div>
          <div className="eyebrow">Production</div>
          <h1 className="hero-title">Build finished products</h1>
          <p className="hero-description">Produce composite goods from BOM and automatically deduct required components.</p>
        </div>
        <span className="badge">{items.length} orders</span>
      </section>

      <section className="resource-layout operation-resource-layout">
        <article className="panel">
          <div className="panel-header"><h2 className="section-title">New production order</h2></div>
          <form onSubmit={onSubmit} className="form-grid">
            <select name="finishedProductId" required defaultValue="">
              <option value="" disabled>Select Finished Product</option>
              {products.map((product) => (
                <option key={product.id} value={product.id}>{product.sku} - {product.name}</option>
              ))}
            </select>
            <input name="quantity" placeholder="Quantity" type="number" step="0.001" required />
            <button type="submit" disabled={isSubmitting}>{isSubmitting ? "Creating..." : "Create Production Order"}</button>
          </form>
          {error && <p className="error-text">{error}</p>}
          {successMessage && <p className="success-text">{successMessage}</p>}
        </article>

        <article className="panel history-panel">
          <div className="panel-header"><h2 className="section-title">Production history</h2></div>
          <table className="table">
            <thead><tr><th>Finished Product</th><th>Quantity</th><th>Created At</th></tr></thead>
            <tbody>
              {items.length === 0 ? (
                <tr><td colSpan={3} className="empty-cell">No production orders yet.</td></tr>
              ) : (
                items.map((item) => (
                  <tr key={item.id}>
                    <td>
                      {item.finishedProduct
                        ? `${item.finishedProduct.sku} - ${item.finishedProduct.name}`
                        : item.finishedProductId}
                    </td>
                    <td><strong>{item.quantity}</strong></td>
                    <td>{new Date(item.createdAt).toLocaleString()}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </article>
      </section>
    </main>
  );
}
