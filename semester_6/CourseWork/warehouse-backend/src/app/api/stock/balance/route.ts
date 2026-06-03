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
    },
    orderBy: { createdAt: "desc" },
  });

  const grouped = await prisma.inventoryTransaction.groupBy({
    by: ["productId"],
    _sum: {
      quantity: true,
    },
  });

  const totals = new Map<string, string>();
  for (const item of grouped) {
    totals.set(item.productId, item._sum.quantity?.toString() ?? "0");
  }

  return NextResponse.json(
    products.map((product) => ({
      ...product,
      quantity: totals.get(product.id) ?? "0",
    })),
  );
}
