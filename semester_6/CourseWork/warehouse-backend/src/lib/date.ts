export function parseOptionalDate(value: string | null, field: string): Date | null {
  if (!value) {
    return null;
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    throw new Error(`Invalid '${field}' date.`);
  }

  return date;
}
