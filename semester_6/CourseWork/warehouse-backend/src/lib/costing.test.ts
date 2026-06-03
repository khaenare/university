import assert from "node:assert/strict";
import test from "node:test";

import { Prisma } from "@prisma/client";

import { calculateProductionCost, CostingValidationError, getWeightedAverageCost } from "@/lib/costing";

test("getWeightedAverageCost calculates weighted average", async () => {
  const tx = {
    receiptLine: {
      findMany: async () => [
        { quantity: new Prisma.Decimal("2"), purchasePrice: new Prisma.Decimal("10") },
        { quantity: new Prisma.Decimal("3"), purchasePrice: new Prisma.Decimal("20") },
      ],
    },
  } as never;

  const result = await getWeightedAverageCost(tx, "p-1");
  assert.equal(result.toString(), "16");
});

test("getWeightedAverageCost throws without purchase history", async () => {
  const tx = {
    receiptLine: {
      findMany: async () => [],
    },
  } as never;

  await assert.rejects(() => getWeightedAverageCost(tx, "p-1"), CostingValidationError);
});

test("getWeightedAverageCost throws for invalid total quantity", async () => {
  const tx = {
    receiptLine: {
      findMany: async () => [
        { quantity: new Prisma.Decimal("0"), purchasePrice: new Prisma.Decimal("10") },
      ],
    },
  } as never;

  await assert.rejects(() => getWeightedAverageCost(tx, "p-1"), CostingValidationError);
});

test("calculateProductionCost returns details and total", async () => {
  const tx = {
    receiptLine: {
      findMany: async ({ where }: { where: { productId: string } }) => {
        if (where.productId === "c-1") {
          return [{ quantity: new Prisma.Decimal("2"), purchasePrice: new Prisma.Decimal("10") }];
        }

        return [{ quantity: new Prisma.Decimal("4"), purchasePrice: new Prisma.Decimal("5") }];
      },
    },
  } as never;

  const result = await calculateProductionCost(tx, [
    { componentId: "c-1", quantity: new Prisma.Decimal("3") },
    { componentId: "c-2", quantity: new Prisma.Decimal("2") },
  ]);

  assert.equal(result.totalCost.toString(), "40");
  assert.equal(result.details.length, 2);
});
