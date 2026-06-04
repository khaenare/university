import {
  CreateProductionOrderPayload,
  CreateProductionRecipePayload,
  CreateReceiptPayload,
  CreateWriteOffPayload,
} from "@/lib/api";

export function buildReceiptPayload(formData: FormData): CreateReceiptPayload {
  const supplierId = String(formData.get("supplierId") ?? "");
  const invoiceNumber = String(formData.get("invoiceNumber") ?? "").trim();
  const invoiceDateRaw = String(formData.get("invoiceDate") ?? "");
  const productIds = formData.getAll("productId").map((value) => String(value));
  const quantities = formData.getAll("quantity").map((value) => Number(value));
  const purchasePrices = formData.getAll("purchasePrice").map((value) => Number(value));

  if (!supplierId) {
    throw new Error("Please select supplier.");
  }

  if (productIds.length === 0) {
    throw new Error("At least one receipt line is required.");
  }

  if (!invoiceNumber) {
    throw new Error("Invoice number is required.");
  }

  if (!invoiceDateRaw) {
    throw new Error("Invoice date is required.");
  }

  const lines = productIds.map((productId, index) => {
    const quantity = quantities[index] ?? 0;
    const purchasePrice = purchasePrices[index] ?? -1;

    if (!productId) {
      throw new Error(`Please select product for line ${index + 1}.`);
    }

    if (!Number.isFinite(quantity) || quantity <= 0) {
      throw new Error(`Quantity in line ${index + 1} must be greater than zero.`);
    }

    if (!Number.isFinite(purchasePrice) || purchasePrice < 0) {
      throw new Error(`Purchase price in line ${index + 1} must be zero or greater.`);
    }

    return { productId, quantity, purchasePrice };
  });

  const uniqueProductIds = new Set(lines.map((line) => line.productId));
  if (uniqueProductIds.size !== lines.length) {
    throw new Error("Receipt lines must have unique products.");
  }

  return {
    supplierId,
    invoiceNumber,
    invoiceDate: new Date(invoiceDateRaw).toISOString(),
    lines,
  };
}

export function buildProductionRecipePayload(formData: FormData): CreateProductionRecipePayload {
  const finishedProductId = String(formData.get("finishedProductId") ?? "");
  const componentIds = formData.getAll("componentId").map((value) => String(value));
  const quantities = formData.getAll("componentQuantity").map((value) => Number(value));

  if (!finishedProductId) {
    throw new Error("Please select a finished product.");
  }

  if (componentIds.length === 0) {
    throw new Error("At least one component is required.");
  }

  const items = componentIds.map((componentId, index) => {
    const quantity = quantities[index] ?? 0;

    if (!componentId) {
      throw new Error(`Please select component for line ${index + 1}.`);
    }

    if (!Number.isFinite(quantity) || quantity <= 0) {
      throw new Error(`Component quantity in line ${index + 1} must be greater than zero.`);
    }

    return { componentId, quantity };
  });

  const uniqueComponentIds = new Set(items.map((item) => item.componentId));
  if (uniqueComponentIds.size !== items.length) {
    throw new Error("Recipe components must be unique.");
  }

  return { finishedProductId, items };
}

export function buildWriteOffPayload(formData: FormData): CreateWriteOffPayload {
  const reasonRaw = String(formData.get("reason") ?? "SALE");
  if (reasonRaw !== "SALE") {
    throw new Error("Write-off reason must be SALE.");
  }
  const reason = reasonRaw;
  const productIds = formData.getAll("productId").map((value) => String(value));
  const quantities = formData.getAll("quantity").map((value) => Number(value));

  if (productIds.length === 0) {
    throw new Error("At least one write-off line is required.");
  }

  const lines = productIds.map((productId, index) => {
    const quantity = quantities[index] ?? 0;

    if (!productId) {
      throw new Error(`Please select product for line ${index + 1}.`);
    }

    if (!Number.isFinite(quantity) || quantity <= 0) {
      throw new Error(`Quantity in line ${index + 1} must be greater than zero.`);
    }

    return { productId, quantity };
  });

  const uniqueProductIds = new Set(lines.map((line) => line.productId));
  if (uniqueProductIds.size !== lines.length) {
    throw new Error("Write-off lines must have unique products.");
  }

  return {
    reason,
    lines,
  };
}

export function buildProductionOrderPayload(formData: FormData): CreateProductionOrderPayload {
  const finishedProductId = String(formData.get("finishedProductId") ?? "");
  const quantity = Number(formData.get("quantity") ?? 0);

  if (!finishedProductId) {
    throw new Error("Please select a finished product.");
  }

  if (!Number.isFinite(quantity) || quantity <= 0) {
    throw new Error("Quantity must be greater than zero.");
  }

  return {
    finishedProductId,
    quantity,
  };
}
