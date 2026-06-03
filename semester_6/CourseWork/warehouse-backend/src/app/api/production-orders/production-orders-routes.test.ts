import assert from "node:assert/strict";
import test from "node:test";

import { Prisma } from "@prisma/client";
import { NextRequest } from "next/server";

import { GET as getProductionOrderById } from "@/app/api/production-orders/[id]/route";
import { POST as createProductionOrder } from "@/app/api/production-orders/route";
import { createAccessToken } from "@/lib/auth";
import { prisma } from "@/lib/prisma";

const managerToken = createAccessToken({ sub: "manager-1", email: "manager@localhost", role: "MANAGER" });

function jsonRequest(url: string, method: string, body?: unknown): NextRequest {
  return new NextRequest(url, {
    method,
    headers: { "content-type": "application/json", authorization: `Bearer ${managerToken}` },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
}

test("POST /api/production-orders returns 400 for invalid quantity", async () => {
  const request = jsonRequest("http://localhost/api/production-orders", "POST", {
    finishedProductId: "f-1",
    quantity: 0,
  });

  const response = await createProductionOrder(request);
  assert.equal(response.status, 400);
});

test("POST /api/production-orders requires an authenticated operator", async () => {
  const response = await createProductionOrder(
    new NextRequest("http://localhost/api/production-orders", { method: "POST" }),
  );
  assert.equal(response.status, 401);
});

test("POST /api/production-orders creates output and component deductions", async () => {
  const originalTransaction = prisma.$transaction;

  prisma.$transaction = async (callback) => {
    const calls = {
      outputType: "",
      issueType: "",
      issueQuantity: "",
      sourceDocument: "",
    };

    const tx = {
      product: {
        findUnique: async ({ where }: { where: { id: string } }) => {
          if (where.id === "f-1") {
            return { id: "f-1", type: "FINISHED" };
          }

          return null;
        },
        findMany: async () => [{ id: "c-1", type: "COMPONENT" }],
      },
      bom: {
        findUnique: async () => ({
          id: "b-1",
          items: [{ componentId: "c-1", quantity: new Prisma.Decimal("2") }],
        }),
      },
      inventoryTransaction: {
        findMany: async () => [{ quantity: new Prisma.Decimal("10") }],
        create: async ({ data }: { data: { type: string; sourceDocument: string } }) => {
          calls.outputType = data.type;
          calls.sourceDocument = data.sourceDocument;
          return { id: "t-out" };
        },
        createMany: async ({ data }: { data: Array<{ type: string; quantity: Prisma.Decimal }> }) => {
          calls.issueType = data[0]?.type ?? "";
          calls.issueQuantity = data[0]?.quantity.toString() ?? "";
          return { count: data.length };
        },
      },
      productionOrder: {
        create: async () => ({ id: "po-1" }),
        findUnique: async () => ({ id: "po-1", items: [] }),
      },
      receiptLine: {
        findMany: async () => [{ quantity: new Prisma.Decimal("10"), purchasePrice: new Prisma.Decimal("5") }],
      },
      costSnapshot: {
        create: async () => ({ id: "cs-1" }),
      },
    } as never;

    const result = await callback(tx);
    assert.equal(calls.outputType, "PRODUCTION_OUTPUT");
    assert.equal(calls.issueType, "ISSUE_PRODUCTION");
    assert.equal(calls.issueQuantity, "-6");
    assert.equal(calls.sourceDocument, "production:po-1");
    return result;
  };

  try {
    const request = jsonRequest("http://localhost/api/production-orders", "POST", {
      finishedProductId: "f-1",
      quantity: 3,
    });

    const response = await createProductionOrder(request);
    assert.equal(response.status, 201);
  } finally {
    prisma.$transaction = originalTransaction;
  }
});

test("POST /api/production-orders returns 400 when finished product is missing", async () => {
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
    const request = jsonRequest("http://localhost/api/production-orders", "POST", {
      finishedProductId: "missing",
      quantity: 1,
    });

    const response = await createProductionOrder(request);
    assert.equal(response.status, 400);
  } finally {
    prisma.$transaction = originalTransaction;
  }
});

test("POST /api/production-orders returns 400 when BOM is missing", async () => {
  const originalTransaction = prisma.$transaction;
  prisma.$transaction = async (callback) => {
    const tx = {
      product: {
        findUnique: async () => ({ id: "f-1", type: "FINISHED" }),
        findMany: async () => [],
      },
      bom: {
        findUnique: async () => null,
      },
    } as never;

    return callback(tx);
  };

  try {
    const request = jsonRequest("http://localhost/api/production-orders", "POST", {
      finishedProductId: "f-1",
      quantity: 1,
    });

    const response = await createProductionOrder(request);
    assert.equal(response.status, 400);
  } finally {
    prisma.$transaction = originalTransaction;
  }
});

test("POST /api/production-orders returns 400 when component stock is insufficient", async () => {
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
      inventoryTransaction: {
        findMany: async () => [{ quantity: new Prisma.Decimal("1") }],
      },
    } as never;

    return callback(tx);
  };

  try {
    const request = jsonRequest("http://localhost/api/production-orders", "POST", {
      finishedProductId: "f-1",
      quantity: 1,
    });

    const response = await createProductionOrder(request);
    assert.equal(response.status, 400);
  } finally {
    prisma.$transaction = originalTransaction;
  }
});

test("POST /api/production-orders returns 400 when component type is invalid", async () => {
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
    const request = jsonRequest("http://localhost/api/production-orders", "POST", {
      finishedProductId: "f-1",
      quantity: 1,
    });

    const response = await createProductionOrder(request);
    assert.equal(response.status, 400);
  } finally {
    prisma.$transaction = originalTransaction;
  }
});

test("POST /api/production-orders returns 400 when BOM component record is missing", async () => {
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
    const request = jsonRequest("http://localhost/api/production-orders", "POST", {
      finishedProductId: "f-1",
      quantity: 1,
    });

    const response = await createProductionOrder(request);
    assert.equal(response.status, 400);
  } finally {
    prisma.$transaction = originalTransaction;
  }
});

test("POST /api/production-orders returns 400 when component purchase history is missing", async () => {
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
          items: [{ componentId: "c-1", quantity: new Prisma.Decimal("1") }],
        }),
      },
      inventoryTransaction: {
        findMany: async () => [{ quantity: new Prisma.Decimal("10") }],
      },
      receiptLine: {
        findMany: async () => [],
      },
    } as never;

    return callback(tx);
  };

  try {
    const request = jsonRequest("http://localhost/api/production-orders", "POST", {
      finishedProductId: "f-1",
      quantity: 1,
    });

    const response = await createProductionOrder(request);
    assert.equal(response.status, 400);
  } finally {
    prisma.$transaction = originalTransaction;
  }
});

test("GET /api/production-orders/[id] returns 404 when missing", async () => {
  const originalFindUnique = prisma.productionOrder.findUnique;
  prisma.productionOrder.findUnique = async () => null;

  try {
    const response = await getProductionOrderById(
      new NextRequest("http://localhost/api/production-orders/po-404", {
        headers: { authorization: `Bearer ${managerToken}` },
      }),
      { params: Promise.resolve({ id: "po-404" }) },
    );
    assert.equal(response.status, 404);
  } finally {
    prisma.productionOrder.findUnique = originalFindUnique;
  }
});
