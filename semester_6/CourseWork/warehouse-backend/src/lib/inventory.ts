import { Prisma } from "@prisma/client";

export class InventoryValidationError extends Error {}

export async function getProductStock(
  tx: Prisma.TransactionClient,
  productId: string,
): Promise<Prisma.Decimal> {
  const rows = await tx.inventoryTransaction.findMany({
    where: { productId },
    select: { quantity: true },
  });

  return rows.reduce((sum, row) => sum.add(row.quantity), new Prisma.Decimal(0));
}

export async function assertSufficientStock(
  tx: Prisma.TransactionClient,
  productId: string,
  issueQuantity: Prisma.Decimal,
): Promise<void> {
  const balance = await getProductStock(tx, productId);

  if (balance.sub(issueQuantity).isNegative()) {
    throw new InventoryValidationError("Insufficient stock for requested operation.");
  }
}
