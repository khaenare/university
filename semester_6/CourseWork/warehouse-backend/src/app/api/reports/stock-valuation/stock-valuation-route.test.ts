import assert from "node:assert/strict";
import test from "node:test";

import { Prisma } from "@prisma/client";
import { NextRequest } from "next/server";

import { GET as getStockValuation } from "@/app/api/reports/stock-valuation/route";
import { createAccessToken } from "@/lib/auth";
import { prisma } from "@/lib/prisma";

const managerToken = createAccessToken({ sub: "manager-1", email: "manager@localhost", role: "MANAGER" });

function authorizedRequest(url: string): NextRequest {
  return new NextRequest(url, { headers: { authorization: `Bearer ${managerToken}` } });
}

test("GET /api/reports/stock-valuation returns valuation summary", async () => {
  const originalFindProducts = prisma.product.findMany;
  const originalGroupBy = prisma.inventoryTransaction.groupBy;
  const originalFindTransactions = prisma.inventoryTransaction.findMany;

  prisma.product.findMany = async () => [{ id: "p-1", sku: "SKU-1", name: "Bolt", unit: "pcs", type: "COMPONENT" }];
  prisma.inventoryTransaction.groupBy = async () => [
    { productId: "p-1", _sum: { quantity: new Prisma.Decimal("10") } },
  ];
  prisma.inventoryTransaction.findMany = async () => [
    { productId: "p-1", unitCost: new Prisma.Decimal("2.5"), createdAt: new Date() },
  ];

  try {
    const response = await getStockValuation(authorizedRequest("http://localhost/api/reports/stock-valuation"));
    assert.equal(response.status, 200);
    const payload = (await response.json()) as { totalValuation: string; items: Array<{ valuation: string }> };
    assert.equal(payload.totalValuation, "25");
    assert.equal(payload.items[0].valuation, "25");
  } finally {
    prisma.product.findMany = originalFindProducts;
    prisma.inventoryTransaction.groupBy = originalGroupBy;
    prisma.inventoryTransaction.findMany = originalFindTransactions;
  }
});
