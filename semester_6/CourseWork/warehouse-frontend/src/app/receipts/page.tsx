"use client";

import { FormEvent, useEffect, useState } from "react";

import { createReceipt, getProducts, getReceipts, getSuppliers, ProductOption, ReceiptItem, SupplierOption } from "@/lib/api";
import { buildReceiptPayload } from "@/lib/form-payloads";

export default function ReceiptsPage() {
  const [items, setItems] = useState<ReceiptItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [suppliers, setSuppliers] = useState<SupplierOption[]>([]);
  const [products, setProducts] = useState<ProductOption[]>([]);
  const [lineIds, setLineIds] = useState([0]);

  async function load() {
    const [receiptsResponse, supplierResponse, productsResponse] = await Promise.all([
      getReceipts(),
      getSuppliers(),
      getProducts(),
    ]);
    setItems(receiptsResponse.items);
    setSuppliers(supplierResponse);
    setProducts(productsResponse);
  }

  useEffect(() => {
    const timer = setTimeout(() => {
      void load().catch((loadError) => {
        setError(loadError instanceof Error ? loadError.message : "Failed to load receipts.");
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

      await createReceipt(buildReceiptPayload(formData));

      form.reset();
      setLineIds([Date.now()]);
      await load();
      setSuccessMessage("Receipt created successfully.");
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Failed to create receipt.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="page-container">
      <section className="hero-card">
        <div>
          <div className="eyebrow">Receipts</div>
          <h1 className="hero-title">Register incoming supplies</h1>
          <p className="hero-description">Add supplier invoices and immediately place received goods on warehouse balance.</p>
        </div>
        <span className="badge">{items.length} receipts</span>
      </section>

      <section className="resource-layout receipt-resource-layout">
        <article className="panel">
          <div className="panel-header">
            <h2 className="section-title">New receipt</h2>
          </div>
          <form onSubmit={onSubmit} className="form-grid">
            <select name="supplierId" required defaultValue="">
              <option value="" disabled>Select Supplier</option>
              {suppliers.map((supplier) => (
                <option key={supplier.id} value={supplier.id}>{supplier.name}</option>
              ))}
            </select>
            <input name="invoiceNumber" placeholder="Invoice Number" required />
            <input name="invoiceDate" type="datetime-local" required />
            <div className="line-list">
              {lineIds.map((lineId, index) => (
                <div className="receipt-form-line" key={lineId}>
                  <select name="productId" required defaultValue="">
                    <option value="" disabled>Select Product</option>
                    {products.map((product) => (
                      <option key={product.id} value={product.id}>{product.sku} - {product.name}</option>
                    ))}
                  </select>
                  <input name="quantity" placeholder="Quantity" type="number" step="0.001" required />
                  <input name="purchasePrice" placeholder="Purchase Price" type="number" step="0.01" required />
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
            <button type="submit" disabled={isSubmitting}>{isSubmitting ? "Creating..." : "Create Receipt"}</button>
          </form>
          {error && <p className="error-text">{error}</p>}
          {successMessage && <p className="success-text">{successMessage}</p>}
        </article>

        <article className="panel">
          <div className="panel-header">
            <h2 className="section-title">Receipt history</h2>
          </div>
          <table className="table">
            <thead>
              <tr><th>Supplier</th><th>Invoice</th><th>Date</th><th>Lines</th></tr>
            </thead>
            <tbody>
              {items.length === 0 ? (
                <tr><td colSpan={4} className="empty-cell">No receipts yet.</td></tr>
              ) : (
                items.map((item) => (
                  <tr key={item.id}>
                    <td>{item.supplier?.name ?? item.supplierId}</td>
                    <td><strong>{item.invoiceNumber}</strong></td>
                    <td>{new Date(item.invoiceDate).toLocaleDateString()}</td>
                    <td className="line-list">
                      {item.lines?.map((line) => (
                        <div key={`${item.id}-${line.product?.id ?? line.product?.sku ?? line.quantity}`}>
                          {line.product ? `${line.product.sku} - ${line.product.name}` : "Product"}: {line.quantity} × {line.purchasePrice}
                        </div>
                      )) ?? "-"}
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
