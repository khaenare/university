import assert from "node:assert/strict";
import test from "node:test";

import { Prisma } from "@prisma/client";
import { NextRequest } from "next/server";

import { DELETE as deleteReceipt, GET as getReceiptById } from "@/app/api/receipts/[id]/route";
import { POST as createReceipt } from "@/app/api/receipts/route";
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

test("POST /api/receipts returns 400 for empty lines", async () => {
  const request = jsonRequest("http://localhost/api/receipts", "POST", {
    supplierId: "s-1",
    invoiceNumber: "INV-1",
    invoiceDate: "2026-01-01T00:00:00.000Z",
    lines: [],
  });

  const response = await createReceipt(request);
  assert.equal(response.status, 400);
});

test("POST /api/receipts requires an authenticated operator", async () => {
  const response = await createReceipt(new NextRequest("http://localhost/api/receipts", { method: "POST" }));
  assert.equal(response.status, 401);
});

test("POST /api/receipts returns 400 for invalid invoice date", async () => {
  const request = jsonRequest("http://localhost/api/receipts", "POST", {
    supplierId: "s-1",
    invoiceNumber: "INV-1",
    invoiceDate: "invalid",
    lines: [{ productId: "p-1", quantity: 1, purchasePrice: 10 }],
  });

  const response = await createReceipt(request);
  assert.equal(response.status, 400);
});

test("POST /api/receipts returns 201 and creates inventory transactions", async () => {
  const originalTransaction = prisma.$transaction;

  prisma.$transaction = async (callback) => {
    const calls = {
      createManyCalled: false,
      sourceDocument: "",
    };

    const tx = {
      supplier: {
        findUnique: async () => ({ id: "s-1" }),
      },
      product: {
        findMany: async () => [{ id: "p-1", type: "COMPONENT" }],
      },
      receipt: {
        create: async () => ({ id: "r-1" }),
        findUnique: async () => ({ id: "r-1", lines: [{ productId: "p-1" }] }),
      },
      inventoryTransaction: {
        createMany: async ({ data }: { data: Array<{ sourceDocument: string }> }) => {
          calls.createManyCalled = true;
          calls.sourceDocument = data[0]?.sourceDocument ?? "";
          return { count: data.length };
        },
      },
    } as never;

    const result = await callback(tx);
    assert.equal(calls.createManyCalled, true);
    assert.equal(calls.sourceDocument, "receipt:r-1");
    return result;
  };

  try {
    const request = jsonRequest("http://localhost/api/receipts", "POST", {
      supplierId: "s-1",
      invoiceNumber: "INV-1",
      invoiceDate: "2026-01-01T00:00:00.000Z",
      lines: [{ productId: "p-1", quantity: 1, purchasePrice: 10 }],
    });

    const response = await createReceipt(request);
    assert.equal(response.status, 201);
  } finally {
    prisma.$transaction = originalTransaction;
  }
});

test("GET /api/receipts/[id] returns 404 when receipt is missing", async () => {
  const originalFindUnique = prisma.receipt.findUnique;
  prisma.receipt.findUnique = async () => null;

  try {
    const response = await getReceiptById(new NextRequest("http://localhost/api/receipts/r-404", {
      headers: { authorization: `Bearer ${managerToken}` },
    }), {
      params: Promise.resolve({ id: "r-404" }),
    });
    assert.equal(response.status, 404);
  } finally {
    prisma.receipt.findUnique = originalFindUnique;
  }
});

test("DELETE /api/receipts/[id] removes receipt and receipt inventory movements", async () => {
  const originalTransaction = prisma.$transaction;
  let isolationLevel: Prisma.TransactionIsolationLevel | undefined;

  prisma.$transaction = async (callback, options) => {
    isolationLevel = options?.isolationLevel;
    const calls = { sourceDocument: "", receiptId: "" };
    const tx = {
      receipt: {
        findUnique: async () => ({ id: "r-1", lines: [{ productId: "p-1", quantity: new Prisma.Decimal("2") }] }),
        delete: async ({ where }: { where: { id: string } }) => {
          calls.receiptId = where.id;
          return { id: where.id };
        },
      },
      inventoryTransaction: {
        findMany: async () => [{ quantity: new Prisma.Decimal("5") }],
        deleteMany: async ({ where }: { where: { sourceDocument: string } }) => {
          calls.sourceDocument = where.sourceDocument;
          return { count: 1 };
        },
      },
    } as never;

    const result = await callback(tx);
    assert.equal(calls.sourceDocument, "receipt:r-1");
    assert.equal(calls.receiptId, "r-1");
    return result;
  };

  try {
    const response = await deleteReceipt(new NextRequest("http://localhost/api/receipts/r-1", {
      method: "DELETE",
      headers: { authorization: `Bearer ${managerToken}` },
    }), { params: Promise.resolve({ id: "r-1" }) });

    assert.equal(response.status, 204);
    assert.equal(isolationLevel, Prisma.TransactionIsolationLevel.Serializable);
  } finally {
    prisma.$transaction = originalTransaction;
  }
});

test("DELETE /api/receipts/[id] maps serialization conflict to 409", async () => {
  const originalTransaction = prisma.$transaction;
  const error = Object.create(Prisma.PrismaClientKnownRequestError.prototype) as Prisma.PrismaClientKnownRequestError;
  Object.assign(error, { code: "P2034" });

  prisma.$transaction = async () => {
    throw error;
  };

  try {
    const response = await deleteReceipt(new NextRequest("http://localhost/api/receipts/r-1", {
      method: "DELETE",
      headers: { authorization: `Bearer ${managerToken}` },
    }), { params: Promise.resolve({ id: "r-1" }) });

    assert.equal(response.status, 409);
  } finally {
    prisma.$transaction = originalTransaction;
  }
});

test("DELETE /api/receipts/[id] blocks deletion when stock was consumed", async () => {
  const originalTransaction = prisma.$transaction;

  prisma.$transaction = async (callback) => {
    const tx = {
      receipt: {
        findUnique: async () => ({ id: "r-1", lines: [{ productId: "p-1", quantity: new Prisma.Decimal("2") }] }),
      },
      inventoryTransaction: {
        findMany: async () => [{ quantity: new Prisma.Decimal("1") }],
      },
    } as never;

    return callback(tx);
  };

  try {
    const response = await deleteReceipt(new NextRequest("http://localhost/api/receipts/r-1", {
      method: "DELETE",
      headers: { authorization: `Bearer ${managerToken}` },
    }), { params: Promise.resolve({ id: "r-1" }) });

    assert.equal(response.status, 400);
  } finally {
    prisma.$transaction = originalTransaction;
  }
});
