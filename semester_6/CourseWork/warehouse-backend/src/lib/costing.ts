import { Prisma } from "@prisma/client";

export class CostingValidationError extends Error {}

export type ComponentCostRow = {
  componentId: string;
  quantity: Prisma.Decimal;
  averageUnitCost: Prisma.Decimal;
  lineCost: Prisma.Decimal;
};

export async function getWeightedAverageCost(
  tx: Prisma.TransactionClient,
  productId: string,
): Promise<Prisma.Decimal> {
  const rows = await tx.receiptLine.findMany({
    where: { productId },
    select: { quantity: true, purchasePrice: true },
  });

  if (rows.length === 0) {
    throw new CostingValidationError(`No purchase history found for component ${productId}.`);
  }

  const totalQty = rows.reduce((sum, row) => sum.add(row.quantity), new Prisma.Decimal(0));
  if (totalQty.lte(0)) {
    throw new CostingValidationError(`Invalid purchase quantity history for component ${productId}.`);
  }

  const totalCost = rows.reduce(
    (sum, row) => sum.add(row.quantity.mul(row.purchasePrice)),
    new Prisma.Decimal(0),
  );

  return totalCost.div(totalQty);
}

export async function calculateProductionCost(
  tx: Prisma.TransactionClient,
  consumptionLines: Array<{ componentId: string; quantity: Prisma.Decimal }>,
): Promise<{ totalCost: Prisma.Decimal; details: ComponentCostRow[] }> {
  const details: ComponentCostRow[] = [];
  let totalCost = new Prisma.Decimal(0);

  for (const line of consumptionLines) {
    const avgCost = await getWeightedAverageCost(tx, line.componentId);
    const lineCost = line.quantity.mul(avgCost);
    totalCost = totalCost.add(lineCost);

    details.push({
      componentId: line.componentId,
      quantity: line.quantity,
      averageUnitCost: avgCost,
      lineCost,
    });
  }

  return { totalCost, details };
}
