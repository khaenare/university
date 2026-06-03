import { ProductType } from "@prisma/client";

export class ProductValidationError extends Error {}

export function requireProductSku(value: unknown): string {
  if (typeof value !== "string") {
    throw new ProductValidationError("Product SKU must be a string.");
  }

  const trimmed = value.trim();
  if (!trimmed) {
    throw new ProductValidationError("Product SKU is required.");
  }

  return trimmed;
}

export function requireProductName(value: unknown): string {
  if (typeof value !== "string") {
    throw new ProductValidationError("Product name must be a string.");
  }

  const trimmed = value.trim();
  if (!trimmed) {
    throw new ProductValidationError("Product name is required.");
  }

  return trimmed;
}

export function requireProductUnit(value: unknown): string {
  if (typeof value !== "string") {
    throw new ProductValidationError("Product unit must be a string.");
  }

  const trimmed = value.trim();
  if (!trimmed) {
    throw new ProductValidationError("Product unit is required.");
  }

  return trimmed;
}

export function requireProductType(value: unknown): ProductType {
  if (value !== ProductType.COMPONENT && value !== ProductType.FINISHED) {
    throw new ProductValidationError("Product type must be COMPONENT or FINISHED.");
  }

  return value;
}

export function validateOptionalBoolean(value: unknown, fieldName: string): boolean | undefined {
  if (value === undefined) {
    return undefined;
  }

  if (typeof value !== "boolean") {
    throw new ProductValidationError(`${fieldName} must be a boolean.`);
  }

  return value;
}

export function validatePatchString(value: unknown, fieldLabel: string): string | undefined {
  if (value === undefined) {
    return undefined;
  }

  if (typeof value !== "string") {
    throw new ProductValidationError(`${fieldLabel} must be a string.`);
  }

  const trimmed = value.trim();
  if (!trimmed) {
    throw new ProductValidationError(`${fieldLabel} cannot be empty.`);
  }

  return trimmed;
}

export function validatePatchProductType(value: unknown): ProductType | undefined {
  if (value === undefined) {
    return undefined;
  }

  return requireProductType(value);
}
