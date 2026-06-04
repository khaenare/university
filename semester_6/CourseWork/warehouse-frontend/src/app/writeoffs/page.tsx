"use client";

import { FormEvent, useEffect, useState } from "react";

import { createWriteOff, deleteWriteOff, getProducts, getWriteOffs, ProductOption, WriteOffItem } from "@/lib/api";
import { buildWriteOffPayload } from "@/lib/form-payloads";

export default function WriteOffsPage() {
  const [items, setItems] = useState<WriteOffItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [products, setProducts] = useState<ProductOption[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [lineIds, setLineIds] = useState([0]);

  async function load() {
    const [writeOffsResponse, productsResponse] = await Promise.all([getWriteOffs(), getProducts()]);
    setItems(writeOffsResponse.items);
    setProducts(productsResponse);
  }

  useEffect(() => {
    const timer = setTimeout(() => {
      void load().catch((loadError) => {
        setError(loadError instanceof Error ? loadError.message : "Failed to load write-offs.");
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
      await createWriteOff(buildWriteOffPayload(formData));

      form.reset();
      setLineIds([Date.now()]);
      await load();
      setSuccessMessage("Write-off created successfully.");
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Failed to create write-off.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function onDelete(writeOff: WriteOffItem) {
    if (!confirm(`Delete write-off ${writeOff.id}?`)) {
      return;
    }

    try {
      setError(null);
      setSuccessMessage(null);
      await deleteWriteOff(writeOff.id);
      await load();
      setSuccessMessage("Write-off deleted successfully.");
    } catch (deleteError) {
      setError(deleteError instanceof Error ? deleteError.message : "Failed to delete write-off.");
    }
  }

  return (
    <main className="page-container">
      <section className="hero-card">
        <div>
          <div className="eyebrow">Write-Offs</div>
          <h1 className="hero-title">Issue goods from stock</h1>
          <p className="hero-description">Record goods sold from stock while preventing negative warehouse balances.</p>
        </div>
        <span className="badge">{items.length} write-offs</span>
      </section>

      <section className="resource-layout operation-resource-layout">
        <article className="panel">
          <div className="panel-header"><h2 className="section-title">New write-off</h2></div>
          <form onSubmit={onSubmit} className="form-grid">
            <select name="reason" defaultValue="SALE">
              <option value="SALE">SALE</option>
            </select>
            <div className="line-list">
              {lineIds.map((lineId, index) => (
                <div className="writeoff-line" key={lineId}>
                  <select name="productId" required defaultValue="">
                    <option value="" disabled>Select Product</option>
                    {products.map((product) => (
                      <option key={product.id} value={product.id}>{product.sku} - {product.name}</option>
                    ))}
                  </select>
                  <input name="quantity" placeholder="Quantity" type="number" step="0.001" required />
                  <button
                    className="secondary-button"
                    type="button"
                    disabled={lineIds.length === 1}
                    onClick={() => setLineIds((current) => current.filter((id) => id !== lineId))}
                  >
                    Remove
                  </button>
                  <span className="badge">Line {index + 1}</span>
                </div>
              ))}
            </div>
            <button className="secondary-button" type="button" onClick={() => setLineIds((current) => [...current, Date.now()])}>
              Add Line
            </button>
            <button type="submit" disabled={isSubmitting}>{isSubmitting ? "Creating..." : "Create Write-Off"}</button>
          </form>
          {error && <p className="error-text">{error}</p>}
          {successMessage && <p className="success-text">{successMessage}</p>}
        </article>

        <article className="panel history-panel">
          <div className="panel-header"><h2 className="section-title">Write-off history</h2></div>
          <table className="table">
            <thead><tr><th>Reason</th><th>Lines</th><th>Created At</th><th>Actions</th></tr></thead>
            <tbody>
              {items.length === 0 ? (
                <tr><td colSpan={4} className="empty-cell">No write-offs yet.</td></tr>
              ) : (
                items.map((item) => (
                  <tr key={item.id}>
                    <td><span className="badge">{item.reason}</span></td>
                    <td>
                      <div className="line-list">
                        {item.lines?.map((line) => (
                          <div key={`${item.id}-${line.product?.id ?? line.quantity}`}>
                            {line.product ? `${line.product.sku} - ${line.product.name}` : "Product"}: {line.quantity}
                          </div>
                        )) ?? "-"}
                      </div>
                    </td>
                    <td>{new Date(item.createdAt).toLocaleString()}</td>
                    <td className="table-actions">
                      <button className="danger-button" type="button" onClick={() => void onDelete(item)}>Delete</button>
                    </td>
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
