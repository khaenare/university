import assert from "node:assert/strict";
import test from "node:test";

import { Prisma } from "@prisma/client";
import { NextRequest } from "next/server";

import { GET as getProductionCost } from "@/app/api/reports/production-cost/route";
import { createAccessToken } from "@/lib/auth";
import { prisma } from "@/lib/prisma";

const managerToken = createAccessToken({ sub: "manager-1", email: "manager@localhost", role: "MANAGER" });

function authorizedRequest(url: string): NextRequest {
  return new NextRequest(url, { headers: { authorization: `Bearer ${managerToken}` } });
}

test("GET /api/reports/production-cost returns snapshot report", async () => {
  const originalFindMany = prisma.costSnapshot.findMany;
  prisma.costSnapshot.findMany = async () => [
    {
      id: "cs-1",
      productionOrderId: "po-1",
      finishedProduct: { id: "f-1", sku: "F-1", name: "Widget", unit: "pcs" },
      productionOrder: { id: "po-1", quantity: new Prisma.Decimal("3") },
      totalCost: new Prisma.Decimal("30"),
      unitCost: new Prisma.Decimal("10"),
      calculationData: { components: [] },
      createdAt: new Date("2026-01-01T00:00:00.000Z"),
    },
  ] as never;

  try {
    const response = await getProductionCost(
      authorizedRequest("http://localhost/api/reports/production-cost?from=2026-01-01T00:00:00.000Z"),
    );
    assert.equal(response.status, 200);
    const payload = (await response.json()) as { items: Array<{ totalCost: string; outputQuantity: string }> };
    assert.equal(payload.items[0].totalCost, "30");
    assert.equal(payload.items[0].outputQuantity, "3");
  } finally {
    prisma.costSnapshot.findMany = originalFindMany;
  }
});

test("GET /api/reports/production-cost returns 400 for invalid date filter", async () => {
  const response = await getProductionCost(
    authorizedRequest("http://localhost/api/reports/production-cost?from=not-a-date"),
  );

  assert.equal(response.status, 400);
});

test("GET /api/reports/production-cost forwards a bounded limit", async () => {
  const originalFindMany = prisma.costSnapshot.findMany;
  let takeValue: number | undefined;

  prisma.costSnapshot.findMany = async ({ take }: { take?: number }) => {
    takeValue = take;
    return [] as never;
  };

  try {
    const response = await getProductionCost(authorizedRequest("http://localhost/api/reports/production-cost?limit=4"));
    assert.equal(response.status, 200);
    assert.equal(takeValue, 4);
  } finally {
    prisma.costSnapshot.findMany = originalFindMany;
  }
});
