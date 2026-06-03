import assert from "node:assert/strict";
import test from "node:test";

import { Prisma } from "@prisma/client";
import { NextRequest } from "next/server";

import { GET as getMovements } from "@/app/api/reports/movements/route";
import { createAccessToken } from "@/lib/auth";
import { prisma } from "@/lib/prisma";

const managerToken = createAccessToken({ sub: "manager-1", email: "manager@localhost", role: "MANAGER" });

function authorizedRequest(url: string): NextRequest {
  return new NextRequest(url, { headers: { authorization: `Bearer ${managerToken}` } });
}

test("GET /api/reports/movements returns movement rows", async () => {
  const originalFindMany = prisma.inventoryTransaction.findMany;
  prisma.inventoryTransaction.findMany = async () => [
    {
      id: "t-1",
      product: { id: "p-1", sku: "S-1", name: "Bolt", unit: "pcs" },
      type: "RECEIPT",
      quantity: new Prisma.Decimal("5"),
      unitCost: new Prisma.Decimal("2"),
      sourceDocument: "receipt:r-1",
      createdAt: new Date("2026-01-01T00:00:00.000Z"),
    },
  ] as never;

  try {
    const response = await getMovements(authorizedRequest("http://localhost/api/reports/movements"));
    assert.equal(response.status, 200);
    const payload = (await response.json()) as { items: Array<{ quantity: string; unitCost: string | null }> };
    assert.equal(payload.items[0].quantity, "5");
    assert.equal(payload.items[0].unitCost, "2");
  } finally {
    prisma.inventoryTransaction.findMany = originalFindMany;
  }
});

test("GET /api/reports/movements returns 400 for invalid date filter", async () => {
  const response = await getMovements(authorizedRequest("http://localhost/api/reports/movements?to=bad-date"));
  assert.equal(response.status, 400);
});

test("GET /api/reports/movements forwards a bounded limit", async () => {
  const originalFindMany = prisma.inventoryTransaction.findMany;
  let takeValue: number | undefined;

  prisma.inventoryTransaction.findMany = async ({ take }: { take?: number }) => {
    takeValue = take;
    return [] as never;
  };

  try {
    const response = await getMovements(authorizedRequest("http://localhost/api/reports/movements?limit=1000"));
    assert.equal(response.status, 200);
    assert.equal(takeValue, 100);
  } finally {
    prisma.inventoryTransaction.findMany = originalFindMany;
  }
});
