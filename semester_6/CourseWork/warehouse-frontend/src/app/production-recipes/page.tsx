"use client";

import { FormEvent, useEffect, useState } from "react";

import {
  createProduct,
  createProductionRecipe,
  getProducts,
  getProductionRecipes,
  ProductOption,
  ProductionRecipeItem,
} from "@/lib/api";
import { buildProductionRecipePayload } from "@/lib/form-payloads";

export default function ProductionRecipesPage() {
  const [recipes, setRecipes] = useState<ProductionRecipeItem[]>([]);
  const [products, setProducts] = useState<ProductOption[]>([]);
  const [lineIds, setLineIds] = useState([0]);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isCreatingProduct, setIsCreatingProduct] = useState(false);
  const [finishedProductId, setFinishedProductId] = useState("");

  const finishedProducts = products.filter((product) => product.type === "FINISHED");
  const componentProducts = products.filter((product) => product.type === "COMPONENT");

  async function load() {
    const [recipesResponse, productsResponse] = await Promise.all([getProductionRecipes(), getProducts()]);
    setRecipes(recipesResponse);
    setProducts(productsResponse);
  }

  useEffect(() => {
    const timer = setTimeout(() => {
      void load().catch((loadError) => {
        setError(loadError instanceof Error ? loadError.message : "Failed to load production recipes.");
      });
    }, 0);

    return () => clearTimeout(timer);
  }, []);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const formData = new FormData(form);

    try {
      setIsSubmitting(true);
      setError(null);
      setSuccessMessage(null);

      await createProductionRecipe(buildProductionRecipePayload(formData));
      form.reset();
      setLineIds([Date.now()]);
      await load();
      setSuccessMessage("Production recipe created successfully.");
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Failed to create production recipe.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function onCreateFinishedProduct(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const formData = new FormData(form);

    try {
      setIsCreatingProduct(true);
      setError(null);
      setSuccessMessage(null);

      const product = await createProduct({
        sku: String(formData.get("finishedSku") ?? "").trim(),
        name: String(formData.get("finishedName") ?? "").trim(),
        unit: String(formData.get("finishedUnit") ?? "").trim(),
        type: "FINISHED",
        isActive: formData.get("finishedIsActive") === "on",
      });

      form.reset();
      await load();
      setFinishedProductId(product.id);
      setSuccessMessage("Finished product created. You can now define its recipe.");
    } catch (createError) {
      setError(createError instanceof Error ? createError.message : "Failed to create finished product.");
    } finally {
      setIsCreatingProduct(false);
    }
  }

  return (
    <main className="page-container">
      <section className="hero-card">
        <div>
          <div className="eyebrow">Recipes</div>
          <h1 className="hero-title">Production recipes</h1>
          <p className="hero-description">Define which components are required to manufacture one unit of a finished product.</p>
        </div>
        <span className="badge">{recipes.length} recipes</span>
      </section>

      <section className="resource-layout recipe-resource-layout">
        <article className="panel">
          <div className="panel-header"><h2 className="section-title">New finished product</h2></div>
          <form className="form-grid" onSubmit={onCreateFinishedProduct}>
            <input name="finishedSku" placeholder="Finished product SKU" required />
            <input name="finishedName" placeholder="Finished product name" required />
            <input name="finishedUnit" placeholder="Unit, e.g. pcs" required />
            <label className="checkbox-row">
              <input name="finishedIsActive" type="checkbox" defaultChecked /> Active
            </label>
            <button type="submit" disabled={isCreatingProduct}>{isCreatingProduct ? "Creating..." : "Create Finished Product"}</button>
          </form>

          <div className="panel-header"><h2 className="section-title">New recipe</h2></div>
          <form className="form-grid" onSubmit={onSubmit}>
            <select name="finishedProductId" required value={finishedProductId} onChange={(event) => setFinishedProductId(event.target.value)}>
              <option value="" disabled>Select Finished Product</option>
              {finishedProducts.map((product) => (
                <option key={product.id} value={product.id}>{product.sku} - {product.name}</option>
              ))}
            </select>
            <div className="line-list">
              {lineIds.map((lineId, index) => (
                <div className="recipe-component-line" key={lineId}>
                  <select name="componentId" required defaultValue="">
                    <option value="" disabled>Select Component</option>
                    {componentProducts.map((product) => (
                      <option key={product.id} value={product.id}>{product.sku} - {product.name}</option>
                    ))}
                  </select>
                  <input name="componentQuantity" placeholder="Qty per unit" type="number" step="0.001" required />
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
              Add Component
            </button>
            <button type="submit" disabled={isSubmitting}>{isSubmitting ? "Creating..." : "Create Recipe"}</button>
          </form>
          {error && <p className="error-text">{error}</p>}
          {successMessage && <p className="success-text">{successMessage}</p>}
        </article>

        <article className="panel">
          <div className="panel-header"><h2 className="section-title">Recipe list</h2></div>
          <table className="table">
            <thead><tr><th>Finished Product</th><th>Components</th></tr></thead>
            <tbody>
              {recipes.length === 0 ? (
                <tr><td colSpan={2} className="empty-cell">No production recipes yet.</td></tr>
              ) : (
                recipes.map((recipe) => (
                  <tr key={recipe.id}>
                    <td>{recipe.finishedProduct ? `${recipe.finishedProduct.sku} - ${recipe.finishedProduct.name}` : recipe.finishedProductId}</td>
                    <td className="line-list">
                      {recipe.items.map((item) => (
                        <div key={`${recipe.id}-${item.componentId}`}>
                          {item.component ? `${item.component.sku} - ${item.component.name}` : item.componentId}: {item.quantity}
                        </div>
                      ))}
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
