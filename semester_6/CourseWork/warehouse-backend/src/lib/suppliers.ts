export class SupplierValidationError extends Error {}

export function normalizeOptionalString(value: unknown): string | null {
  if (value === undefined || value === null) {
    return null;
  }

  if (typeof value !== "string") {
    throw new SupplierValidationError("Optional supplier fields must be strings or null.");
  }

  const trimmed = value.trim();
  return trimmed.length > 0 ? trimmed : null;
}

export function requireSupplierName(value: unknown): string {
  if (typeof value !== "string") {
    throw new SupplierValidationError("Supplier name must be a string.");
  }

  const trimmed = value.trim();

  if (!trimmed) {
    throw new SupplierValidationError("Supplier name is required.");
  }

  return trimmed;
}

export function validateSupplierPatchName(value: unknown): string | undefined {
  if (value === undefined) {
    return undefined;
  }

  if (typeof value !== "string") {
    throw new SupplierValidationError("Supplier name must be a string.");
  }

  const trimmed = value.trim();

  if (!trimmed) {
    throw new SupplierValidationError("Supplier name cannot be empty.");
  }

  return trimmed;
}
