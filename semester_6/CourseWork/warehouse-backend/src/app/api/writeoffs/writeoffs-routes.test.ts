import assert from "node:assert/strict";
import test from "node:test";

import { Prisma } from "@prisma/client";
import { NextRequest } from "next/server";

import { GET as getWriteOffById } from "@/app/api/writeoffs/[id]/route";
import { POST as createWriteOff } from "@/app/api/writeoffs/route";
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

test("POST /api/writeoffs returns 400 for invalid reason", async () => {
  const request = jsonRequest("http://localhost/api/writeoffs", "POST", {
    reason: "OTHER",
    lines: [{ productId: "p-1", quantity: 1 }],
  });

  const response = await createWriteOff(request);
  assert.equal(response.status, 400);
});

test("POST /api/writeoffs requires an authenticated operator", async () => {
  const response = await createWriteOff(new NextRequest("http://localhost/api/writeoffs", { method: "POST" }));
  assert.equal(response.status, 401);
});

test("POST /api/writeoffs returns 400 on insufficient stock", async () => {
  const originalTransaction = prisma.$transaction;

  prisma.$transaction = async (callback) => {
    const tx = {
      product: {
        findMany: async () => [{ id: "p-1" }],
      },
      inventoryTransaction: {
        findMany: async () => [],
        createMany: async () => ({ count: 1 }),
      },
      writeOff: {
        create: async () => ({ id: "w-1" }),
        findUnique: async () => ({ id: "w-1" }),
      },
    } as never;

    return callback(tx);
  };

  try {
    const request = jsonRequest("http://localhost/api/writeoffs", "POST", {
      reason: "SALE",
      lines: [{ productId: "p-1", quantity: 1 }],
    });
    const response = await createWriteOff(request);
    assert.equal(response.status, 400);
  } finally {
    prisma.$transaction = originalTransaction;
  }
});

test("POST /api/writeoffs creates negative inventory movements", async () => {
  const originalTransaction = prisma.$transaction;

  prisma.$transaction = async (callback) => {
    const calls = {
      createManyCalled: false,
      quantityValue: "",
      sourceDocument: "",
    };

    const tx = {
      product: {
        findMany: async () => [{ id: "p-1" }],
      },
      inventoryTransaction: {
        findMany: async () => [{ quantity: new Prisma.Decimal("5") }],
        createMany: async ({ data }: { data: Array<{ quantity: Prisma.Decimal; sourceDocument: string }> }) => {
          calls.createManyCalled = true;
          calls.quantityValue = data[0]?.quantity.toString() ?? "";
          calls.sourceDocument = data[0]?.sourceDocument ?? "";
          return { count: data.length };
        },
      },
      writeOff: {
        create: async () => ({ id: "w-1" }),
        findUnique: async () => ({ id: "w-1", lines: [{ productId: "p-1" }] }),
      },
    } as never;

    const result = await callback(tx);
    assert.equal(calls.createManyCalled, true);
    assert.equal(calls.quantityValue, "-2");
    assert.equal(calls.sourceDocument, "writeoff:w-1");
    return result;
  };

  try {
    const request = jsonRequest("http://localhost/api/writeoffs", "POST", {
      reason: "SALE",
      lines: [{ productId: "p-1", quantity: 2 }],
    });
    const response = await createWriteOff(request);
    assert.equal(response.status, 201);
  } finally {
    prisma.$transaction = originalTransaction;
  }
});

test("GET /api/writeoffs/[id] returns 404 for missing write-off", async () => {
  const originalFindUnique = prisma.writeOff.findUnique;
  prisma.writeOff.findUnique = async () => null;

  try {
    const response = await getWriteOffById(new NextRequest("http://localhost/api/writeoffs/w-404", {
      headers: { authorization: `Bearer ${managerToken}` },
    }), {
      params: Promise.resolve({ id: "w-404" }),
    });
    assert.equal(response.status, 404);
  } finally {
    prisma.writeOff.findUnique = originalFindUnique;
  }
});
