"use client";

import { FormEvent, useEffect, useState } from "react";

import { createSupplier, deleteSupplier, getSupplierList, SupplierItem, updateSupplier } from "@/lib/api";

function optionalText(formData: FormData, name: string): string | null {
  const value = String(formData.get(name) ?? "").trim();
  return value ? value : null;
}

export default function SuppliersPage() {
  const [items, setItems] = useState<SupplierItem[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function load() {
    const suppliers = await getSupplierList();
    setItems(suppliers);
    setSelectedId((current) => current || suppliers[0]?.id || "");
  }

  useEffect(() => {
    const timer = setTimeout(() => {
      void load().catch((loadError) => {
        setError(loadError instanceof Error ? loadError.message : "Failed to load suppliers.");
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

      await createSupplier({
        name: String(formData.get("name") ?? "").trim(),
        contactName: optionalText(formData, "contactName"),
        contactEmail: optionalText(formData, "contactEmail"),
        contactPhone: optionalText(formData, "contactPhone"),
        address: optionalText(formData, "address"),
      });

      form.reset();
      await load();
      setSuccessMessage("Supplier created successfully.");
    } catch (createError) {
      setError(createError instanceof Error ? createError.message : "Failed to create supplier.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function onUpdate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);

    if (!selectedId) {
      setError("Select a supplier to update.");
      return;
    }

    try {
      setError(null);
      setSuccessMessage(null);
      await updateSupplier(selectedId, {
        name: String(formData.get("editName") ?? "").trim(),
        contactName: optionalText(formData, "editContactName"),
        contactEmail: optionalText(formData, "editContactEmail"),
        contactPhone: optionalText(formData, "editContactPhone"),
        address: optionalText(formData, "editAddress"),
      });
      await load();
      setSuccessMessage("Supplier updated.");
    } catch (updateError) {
      setError(updateError instanceof Error ? updateError.message : "Failed to update supplier.");
    }
  }

  async function onDelete(supplier: SupplierItem) {
    if (!confirm(`Delete supplier ${supplier.name}?`)) {
      return;
    }

    try {
      setError(null);
      setSuccessMessage(null);
      await deleteSupplier(supplier.id);
      await load();
      setSuccessMessage("Supplier deleted.");
    } catch (deleteError) {
      setError(deleteError instanceof Error ? deleteError.message : "Failed to delete supplier.");
    }
  }

  const selectedSupplier = items.find((supplier) => supplier.id === selectedId);

  return (
    <main className="page-container">
      <section className="hero-card">
        <div>
          <div className="eyebrow">Admin</div>
          <h1 className="hero-title">Suppliers</h1>
          <p className="hero-description">Manage supplier master data and contact information.</p>
        </div>
        <span className="badge">{items.length} suppliers</span>
      </section>

      <section className="resource-layout">
        <article className="panel">
          <div className="panel-header"><h2 className="section-title">New supplier</h2></div>
          <form onSubmit={onCreate} className="form-grid">
            <input name="name" placeholder="Supplier name" required />
            <input name="contactName" placeholder="Contact person" />
            <input name="contactEmail" placeholder="Email" type="email" />
            <input name="contactPhone" placeholder="Phone" />
            <input name="address" placeholder="Address" />
            <button type="submit" disabled={isSubmitting}>{isSubmitting ? "Creating..." : "Create supplier"}</button>
          </form>

          <div className="panel-header"><h2 className="section-title">Edit supplier</h2></div>
          <form onSubmit={onUpdate} className="form-grid">
            <select value={selectedId} onChange={(event) => setSelectedId(event.target.value)}>
              {items.map((supplier) => <option key={supplier.id} value={supplier.id}>{supplier.name}</option>)}
            </select>
            <input name="editName" placeholder="Supplier name" required key={`name-${selectedSupplier?.id}`} defaultValue={selectedSupplier?.name ?? ""} />
            <input name="editContactName" placeholder="Contact person" key={`contact-${selectedSupplier?.id}`} defaultValue={selectedSupplier?.contactName ?? ""} />
            <input name="editContactEmail" placeholder="Email" type="email" key={`email-${selectedSupplier?.id}`} defaultValue={selectedSupplier?.contactEmail ?? ""} />
            <input name="editContactPhone" placeholder="Phone" key={`phone-${selectedSupplier?.id}`} defaultValue={selectedSupplier?.contactPhone ?? ""} />
            <input name="editAddress" placeholder="Address" key={`address-${selectedSupplier?.id}`} defaultValue={selectedSupplier?.address ?? ""} />
            <button type="submit" disabled={!selectedSupplier}>Update supplier</button>
          </form>

          {error ? <p className="error-text">{error}</p> : null}
          {successMessage ? <p className="success-text">{successMessage}</p> : null}
        </article>

        <article className="panel">
          <div className="panel-header"><h2 className="section-title">Supplier list</h2></div>
          <table className="table">
            <thead>
              <tr><th>Name</th><th>Contact</th><th>Email</th><th>Phone</th><th>Actions</th></tr>
            </thead>
            <tbody>
              {items.map((supplier) => (
                <tr key={supplier.id}>
                  <td>{supplier.name}</td>
                  <td>{supplier.contactName ?? "-"}</td>
                  <td>{supplier.contactEmail ?? "-"}</td>
                  <td>{supplier.contactPhone ?? "-"}</td>
                  <td className="table-actions">
                    <button className="secondary-button" type="button" onClick={() => setSelectedId(supplier.id)}>Edit</button>
                    <button className="danger-button" type="button" onClick={() => void onDelete(supplier)}>Delete</button>
                  </td>
                </tr>
              ))}
              {items.length === 0 ? <tr><td className="empty-cell" colSpan={5}>No suppliers yet.</td></tr> : null}
            </tbody>
          </table>
        </article>
      </section>
    </main>
  );
}
