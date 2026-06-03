import assert from "node:assert/strict";
import test from "node:test";

import { Prisma } from "@prisma/client";
import { NextRequest } from "next/server";

import { GET as getStockBalance } from "@/app/api/stock/balance/route";
import { createAccessToken } from "@/lib/auth";
import { prisma } from "@/lib/prisma";

const managerToken = createAccessToken({ sub: "manager-1", email: "manager@localhost", role: "MANAGER" });

function authorizedRequest(url: string): NextRequest {
  return new NextRequest(url, { headers: { authorization: `Bearer ${managerToken}` } });
}

test("GET /api/stock/balance returns decimal-safe string quantities", async () => {
  const originalFindMany = prisma.product.findMany;
  const originalGroupBy = prisma.inventoryTransaction.groupBy;

  prisma.product.findMany = async () => [
    { id: "p-1", sku: "SKU-1", name: "Bolt", unit: "pcs" },
    { id: "p-2", sku: "SKU-2", name: "Nut", unit: "pcs" },
  ];

  prisma.inventoryTransaction.groupBy = async () => [
    {
      productId: "p-1",
      _sum: {
        quantity: new Prisma.Decimal("12.34"),
      },
    },
  ];

  try {
    const response = await getStockBalance(authorizedRequest("http://localhost/api/stock/balance"));
    assert.equal(response.status, 200);

    const payload = (await response.json()) as Array<{ id: string; quantity: string }>;
    const first = payload.find((row) => row.id === "p-1");
    const second = payload.find((row) => row.id === "p-2");

    assert.equal(first?.quantity, "12.34");
    assert.equal(second?.quantity, "0");
    assert.equal(typeof first?.quantity, "string");
    assert.equal(typeof second?.quantity, "string");
  } finally {
    prisma.product.findMany = originalFindMany;
    prisma.inventoryTransaction.groupBy = originalGroupBy;
  }
});
