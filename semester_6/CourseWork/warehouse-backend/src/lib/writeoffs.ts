export class WriteOffValidationError extends Error {}

export type WriteOffReasonValue = "SALE";

type WriteOffLineInput = {
  productId?: string;
  quantity?: number;
};

export function requireWriteOffReason(value: unknown): WriteOffReasonValue {
  if (value !== "SALE") {
    throw new WriteOffValidationError("Write-off reason must be SALE.");
  }

  return value;
}

export function requireWriteOffLines(value: unknown): Array<{ productId: string; quantity: number }> {
  if (!Array.isArray(value) || value.length === 0) {
    throw new WriteOffValidationError("Write-off lines must be a non-empty array.");
  }

  const normalized = value.map((line, index) => {
    if (!line || typeof line !== "object" || Array.isArray(line)) {
      throw new WriteOffValidationError(`Line at index ${index} must be an object.`);
    }

    const typedLine = line as WriteOffLineInput;

    if (typeof typedLine.productId !== "string" || !typedLine.productId.trim()) {
      throw new WriteOffValidationError(`Product ID at index ${index} is required.`);
    }

    if (typeof typedLine.quantity !== "number" || !Number.isFinite(typedLine.quantity) || typedLine.quantity <= 0) {
      throw new WriteOffValidationError(`Quantity at index ${index} must be a positive number.`);
    }

    return {
      productId: typedLine.productId.trim(),
      quantity: typedLine.quantity,
    };
  });

  const uniqueIds = new Set(normalized.map((line) => line.productId));
  if (uniqueIds.size !== normalized.length) {
    throw new WriteOffValidationError("Write-off lines must have unique product IDs.");
  }

  return normalized;
}
