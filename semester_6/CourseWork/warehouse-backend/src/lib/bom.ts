import { ProductType } from "@prisma/client";

export class BomValidationError extends Error {}

export type BomItemInput = {
  componentId?: string;
  quantity?: number;
};

export function requireId(value: unknown, fieldLabel: string): string {
  if (typeof value !== "string") {
    throw new BomValidationError(`${fieldLabel} must be a string.`);
  }

  const trimmed = value.trim();
  if (!trimmed) {
    throw new BomValidationError(`${fieldLabel} is required.`);
  }

  return trimmed;
}

export function requireBomItems(value: unknown): Array<{ componentId: string; quantity: number }> {
  if (!Array.isArray(value) || value.length === 0) {
    throw new BomValidationError("BOM items must be a non-empty array.");
  }

  const normalized = value.map((item, index) => {
    if (!item || typeof item !== "object" || Array.isArray(item)) {
      throw new BomValidationError(`BOM item at index ${index} must be an object.`);
    }

    const typedItem = item as BomItemInput;
    const componentId = requireId(typedItem.componentId, `Component ID at index ${index}`);

    if (typeof typedItem.quantity !== "number" || !Number.isFinite(typedItem.quantity)) {
      throw new BomValidationError(`Quantity at index ${index} must be a number.`);
    }

    if (typedItem.quantity <= 0) {
      throw new BomValidationError(`Quantity at index ${index} must be greater than zero.`);
    }

    return {
      componentId,
      quantity: typedItem.quantity,
    };
  });

  const uniqueIds = new Set(normalized.map((item) => item.componentId));
  if (uniqueIds.size !== normalized.length) {
    throw new BomValidationError("BOM items must have unique component IDs.");
  }

  return normalized;
}

export function assertProductType(actual: ProductType, expected: ProductType, message: string): void {
  if (actual !== expected) {
    throw new BomValidationError(message);
  }
}
