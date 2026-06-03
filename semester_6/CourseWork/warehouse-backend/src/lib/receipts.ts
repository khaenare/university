export class ReceiptValidationError extends Error {}

export type ReceiptLineInput = {
  productId?: string;
  quantity?: number;
  purchasePrice?: number;
};

export function requireReceiptId(value: unknown, field: string): string {
  if (typeof value !== "string") {
    throw new ReceiptValidationError(`${field} must be a string.`);
  }

  const trimmed = value.trim();
  if (!trimmed) {
    throw new ReceiptValidationError(`${field} is required.`);
  }

  return trimmed;
}

export function requireInvoiceDate(value: unknown): Date {
  if (typeof value !== "string") {
    throw new ReceiptValidationError("Invoice date must be an ISO string.");
  }

  const isoUtcPattern = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/;
  if (!isoUtcPattern.test(value)) {
    throw new ReceiptValidationError("Invoice date must be in ISO UTC format.");
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    throw new ReceiptValidationError("Invoice date is invalid.");
  }

  if (date.toISOString() !== value) {
    throw new ReceiptValidationError("Invoice date must be a valid ISO UTC timestamp.");
  }

  return date;
}

export function requireReceiptLines(value: unknown): Array<{ productId: string; quantity: number; purchasePrice: number }> {
  if (!Array.isArray(value) || value.length === 0) {
    throw new ReceiptValidationError("Receipt lines must be a non-empty array.");
  }

  const normalized = value.map((line, index) => {
    if (!line || typeof line !== "object" || Array.isArray(line)) {
      throw new ReceiptValidationError(`Line at index ${index} must be an object.`);
    }

    const typed = line as ReceiptLineInput;
    const productId = requireReceiptId(typed.productId, `Product ID at index ${index}`);

    if (typeof typed.quantity !== "number" || !Number.isFinite(typed.quantity) || typed.quantity <= 0) {
      throw new ReceiptValidationError(`Quantity at index ${index} must be a positive number.`);
    }

    if (
      typeof typed.purchasePrice !== "number" ||
      !Number.isFinite(typed.purchasePrice) ||
      typed.purchasePrice < 0
    ) {
      throw new ReceiptValidationError(`Purchase price at index ${index} must be a non-negative number.`);
    }

    return {
      productId,
      quantity: typed.quantity,
      purchasePrice: typed.purchasePrice,
    };
  });

  const uniqueProductIds = new Set(normalized.map((line) => line.productId));
  if (uniqueProductIds.size !== normalized.length) {
    throw new ReceiptValidationError("Receipt lines must have unique product IDs.");
  }

  return normalized;
}
