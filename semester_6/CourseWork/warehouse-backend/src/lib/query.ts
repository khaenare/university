export function parseOptionalLimit(value: string | null, defaultLimit?: number): number | undefined {
  if (value === null) {
    return defaultLimit;
  }

  const parsed = Number(value);

  if (!Number.isInteger(parsed) || parsed < 1) {
    throw new Error("Invalid 'limit' filter. Expected a positive integer.");
  }

  return Math.min(parsed, 100);
}
