"use client";

import { FormEvent, useEffect, useState } from "react";

import { createProduct, deleteProduct, getProducts, ProductOption, updateProduct } from "@/lib/api";

export default function ProductsPage() {
  const [items, setItems] = useState<ProductOption[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function load() {
    const products = await getProducts();
    setItems(products);
  }

  useEffect(() => {
    const timer = setTimeout(() => {
      void load().catch((loadError) => {
        setError(loadError instanceof Error ? loadError.message : "Failed to load products.");
      });
    }, 0);

    return () => {
      clearTimeout(timer);
    };
  }, []);

  async function onCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const formData = new FormData(form);

    try {
      setIsSubmitting(true);
      setError(null);
      setSuccessMessage(null);

      await createProduct({
        sku: String(formData.get("sku") ?? "").trim(),
        name: String(formData.get("name") ?? "").trim(),
        unit: String(formData.get("unit") ?? "").trim(),
        type: "COMPONENT",
        isActive: formData.get("isActive") === "on",
      });

      form.reset();
      await load();
      setSuccessMessage("Product created successfully.");
    } catch (createError) {
      setError(createError instanceof Error ? createError.message : "Failed to create product.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function toggleActive(product: ProductOption) {
    try {
      setError(null);
      setSuccessMessage(null);
      await updateProduct(product.id, { isActive: !product.isActive });
      await load();
      setSuccessMessage("Product status updated.");
    } catch (updateError) {
      setError(updateError instanceof Error ? updateError.message : "Failed to update product.");
    }
  }

  async function onDelete(product: ProductOption) {
    if (!confirm(`Delete product ${product.sku}?`)) {
      return;
    }

    try {
      setError(null);
      setSuccessMessage(null);
      await deleteProduct(product.id);
      await load();
      setSuccessMessage("Product deleted.");
    } catch (deleteError) {
      setError(deleteError instanceof Error ? deleteError.message : "Failed to delete product.");
    }
  }

  const componentItems = items.filter((product) => product.type === "COMPONENT");

  return (
    <main className="page-container">
      <section className="hero-card">
        <div>
          <div className="eyebrow">Admin</div>
          <h1 className="hero-title">Products</h1>
          <p className="hero-description">Manage component master data. Finished products are created from Production Recipes.</p>
        </div>
        <span className="badge">{componentItems.length} components</span>
      </section>

      <section className="resource-layout">
        <article className="panel">
          <div className="panel-header">
            <h2 className="section-title">New product</h2>
          </div>
          <form onSubmit={onCreate} className="form-grid">
            <input name="sku" placeholder="SKU" required />
            <input name="name" placeholder="Product name" required />
            <input name="unit" placeholder="Unit, e.g. pcs" required />
            <input value="Component" disabled aria-label="Product type" />
            <label className="checkbox-row">
              <input name="isActive" type="checkbox" defaultChecked /> Active
            </label>
            <button type="submit" disabled={isSubmitting}>{isSubmitting ? "Creating..." : "Create product"}</button>
          </form>
          {error ? <p className="error-text">{error}</p> : null}
          {successMessage ? <p className="success-text">{successMessage}</p> : null}
        </article>

        <article className="panel">
          <div className="panel-header">
            <h2 className="section-title">Product catalog</h2>
          </div>
          <table className="table">
            <thead>
              <tr>
                <th>SKU</th>
                <th>Name</th>
                <th>Type</th>
                <th>Unit</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {componentItems.map((product) => (
                <tr key={product.id}>
                  <td>{product.sku}</td>
                  <td>{product.name}</td>
                  <td><span className="badge">{product.type}</span></td>
                  <td>{product.unit ?? "-"}</td>
                  <td>{product.isActive ? "Active" : "Inactive"}</td>
                  <td className="table-actions">
                    <button className="secondary-button" type="button" onClick={() => void toggleActive(product)}>
                      {product.isActive ? "Deactivate" : "Activate"}
                    </button>
                    <button className="danger-button" type="button" onClick={() => void onDelete(product)}>Delete</button>
                  </td>
                </tr>
              ))}
              {componentItems.length === 0 ? <tr><td className="empty-cell" colSpan={6}>No components yet.</td></tr> : null}
            </tbody>
          </table>
        </article>
      </section>
    </main>
  );
}
