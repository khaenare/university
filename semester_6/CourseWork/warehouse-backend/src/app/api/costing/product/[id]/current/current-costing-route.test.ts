import assert from "node:assert/strict";
import test from "node:test";

import { Prisma } from "@prisma/client";
import { NextRequest } from "next/server";

import { GET as getCurrentCost } from "@/app/api/costing/product/[id]/current/route";
import { createAccessToken } from "@/lib/auth";
import { prisma } from "@/lib/prisma";

const managerToken = createAccessToken({ sub: "manager-1", email: "manager@localhost", role: "MANAGER" });

function authorizedRequest(url: string): NextRequest {
  return new NextRequest(url, { headers: { authorization: `Bearer ${managerToken}` } });
}

test("GET current cost returns 404 for missing product", async () => {
  const originalTransaction = prisma.$transaction;
  prisma.$transaction = async (callback) => {
    const tx = {
      product: {
        findUnique: async () => null,
      },
    } as never;

    return callback(tx);
  };

  try {
    const response = await getCurrentCost(authorizedRequest("http://localhost/api/costing/product/p-1/current"), {
      params: Promise.resolve({ id: "p-1" }),
    });
    assert.equal(response.status, 404);
  } finally {
    prisma.$transaction = originalTransaction;
  }
});

test("GET current cost returns calculated payload", async () => {
  const originalTransaction = prisma.$transaction;
  prisma.$transaction = async (callback) => {
    const tx = {
      product: {
        findUnique: async () => ({ id: "f-1", type: "FINISHED" }),
        findMany: async () => [{ id: "c-1", type: "COMPONENT" }],
      },
      bom: {
        findUnique: async () => ({
          id: "b-1",
          items: [{ componentId: "c-1", quantity: new Prisma.Decimal("2") }],
        }),
      },
      receiptLine: {
        findMany: async () => [
          { quantity: new Prisma.Decimal("1"), purchasePrice: new Prisma.Decimal("3") },
          { quantity: new Prisma.Decimal("1"), purchasePrice: new Prisma.Decimal("5") },
        ],
      },
    } as never;

    return callback(tx);
  };

  try {
    const response = await getCurrentCost(authorizedRequest("http://localhost/api/costing/product/f-1/current"), {
      params: Promise.resolve({ id: "f-1" }),
    });
    assert.equal(response.status, 200);
    const payload = (await response.json()) as { totalCost: string; unitCost: string; quantityBase: string };
    assert.equal(payload.totalCost, "8");
    assert.equal(payload.unitCost, "8");
    assert.equal(payload.quantityBase, "1");
  } finally {
    prisma.$transaction = originalTransaction;
  }
});

test("GET current cost returns 400 for non-finished product", async () => {
  const originalTransaction = prisma.$transaction;
  prisma.$transaction = async (callback) => {
    const tx = {
      product: {
        findUnique: async () => ({ id: "p-1", type: "COMPONENT" }),
      },
    } as never;

    return callback(tx);
  };

  try {
    const response = await getCurrentCost(authorizedRequest("http://localhost/api/costing/product/p-1/current"), {
      params: Promise.resolve({ id: "p-1" }),
    });
    assert.equal(response.status, 400);
  } finally {
    prisma.$transaction = originalTransaction;
  }
});

test("GET current cost returns 400 when BOM is missing", async () => {
  const originalTransaction = prisma.$transaction;
  prisma.$transaction = async (callback) => {
    const tx = {
      product: {
        findUnique: async () => ({ id: "f-1", type: "FINISHED" }),
      },
      bom: {
        findUnique: async () => null,
      },
    } as never;

    return callback(tx);
  };

  try {
    const response = await getCurrentCost(authorizedRequest("http://localhost/api/costing/product/f-1/current"), {
      params: Promise.resolve({ id: "f-1" }),
    });
    assert.equal(response.status, 400);
  } finally {
    prisma.$transaction = originalTransaction;
  }
});

test("GET current cost returns 400 when BOM component record is missing", async () => {
  const originalTransaction = prisma.$transaction;
  prisma.$transaction = async (callback) => {
    const tx = {
      product: {
        findUnique: async () => ({ id: "f-1", type: "FINISHED" }),
        findMany: async () => [{ id: "c-1", type: "COMPONENT" }],
      },
      bom: {
        findUnique: async () => ({
          id: "b-1",
          items: [
            { componentId: "c-1", quantity: new Prisma.Decimal("1") },
            { componentId: "c-2", quantity: new Prisma.Decimal("1") },
          ],
        }),
      },
    } as never;

    return callback(tx);
  };

  try {
    const response = await getCurrentCost(authorizedRequest("http://localhost/api/costing/product/f-1/current"), {
      params: Promise.resolve({ id: "f-1" }),
    });
    assert.equal(response.status, 400);
  } finally {
    prisma.$transaction = originalTransaction;
  }
});

test("GET current cost returns 400 when BOM component type is invalid", async () => {
  const originalTransaction = prisma.$transaction;
  prisma.$transaction = async (callback) => {
    const tx = {
      product: {
        findUnique: async () => ({ id: "f-1", type: "FINISHED" }),
        findMany: async () => [{ id: "c-1", type: "FINISHED" }],
      },
      bom: {
        findUnique: async () => ({
          id: "b-1",
          items: [{ componentId: "c-1", quantity: new Prisma.Decimal("1") }],
        }),
      },
    } as never;

    return callback(tx);
  };

  try {
    const response = await getCurrentCost(authorizedRequest("http://localhost/api/costing/product/f-1/current"), {
      params: Promise.resolve({ id: "f-1" }),
    });
    assert.equal(response.status, 400);
  } finally {
    prisma.$transaction = originalTransaction;
  }
});
