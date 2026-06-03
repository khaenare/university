export class ProductionOrderValidationError extends Error {}

export function requireProductionProductId(value: unknown): string {
  if (typeof value !== "string") {
    throw new ProductionOrderValidationError("Finished product ID must be a string.");
  }

  const trimmed = value.trim();
  if (!trimmed) {
    throw new ProductionOrderValidationError("Finished product ID is required.");
  }

  return trimmed;
}

export function requireProductionQuantity(value: unknown): number {
  if (typeof value !== "number" || !Number.isFinite(value) || value <= 0) {
    throw new ProductionOrderValidationError("Production quantity must be a positive number.");
  }

  return value;
}
