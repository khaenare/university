import { Prisma } from "@prisma/client";
import { NextRequest, NextResponse } from "next/server";

import { OPERATOR_ROLES, requireRole } from "@/lib/authorization";
import { prisma } from "@/lib/prisma";

export async function GET(request: NextRequest) {
  const authorizationError = requireRole(request, OPERATOR_ROLES);

  if (authorizationError) {
    return authorizationError;
  }

  const products = await prisma.product.findMany({
    select: {
      id: true,
      sku: true,
      name: true,
      unit: true,
      type: true,
    },
    orderBy: { createdAt: "desc" },
  });

  const groupedTransactions = await prisma.inventoryTransaction.groupBy({
    by: ["productId"],
    _sum: { quantity: true },
  });

  const latestCosts = await prisma.inventoryTransaction.findMany({
    where: {
      unitCost: { not: null },
      type: { in: ["RECEIPT", "PRODUCTION_OUTPUT"] },
    },
    orderBy: { createdAt: "desc" },
    select: {
      productId: true,
      unitCost: true,
      createdAt: true,
    },
  });

  const stockByProduct = new Map<string, Prisma.Decimal>();
  for (const row of groupedTransactions) {
    stockByProduct.set(row.productId, row._sum.quantity ?? new Prisma.Decimal(0));
  }

  const unitCostByProduct = new Map<string, Prisma.Decimal>();
  for (const row of latestCosts) {
    if (!unitCostByProduct.has(row.productId) && row.unitCost) {
      unitCostByProduct.set(row.productId, row.unitCost);
    }
  }

  let totalValuation = new Prisma.Decimal(0);
  const items = products.map((product) => {
    const quantity = stockByProduct.get(product.id) ?? new Prisma.Decimal(0);
    const unitCost = unitCostByProduct.get(product.id) ?? new Prisma.Decimal(0);
    const valuation = quantity.mul(unitCost);

    totalValuation = totalValuation.add(valuation);

    return {
      productId: product.id,
      sku: product.sku,
      name: product.name,
      unit: product.unit,
      type: product.type,
      quantity: quantity.toString(),
      unitCost: unitCost.toString(),
      valuation: valuation.toString(),
    };
  });

  return NextResponse.json({
    totalValuation: totalValuation.toString(),
    items,
  });
}
