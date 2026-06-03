import assert from "node:assert/strict";
import test from "node:test";

import { Prisma } from "@prisma/client";
import { NextRequest } from "next/server";

import { POST as createBom } from "@/app/api/bom/route";
import { DELETE as deleteBom, PATCH as updateBom } from "@/app/api/bom/[id]/route";
import { createAccessToken } from "@/lib/auth";
import { prisma } from "@/lib/prisma";

const adminToken = createAccessToken({ sub: "admin-1", email: "admin@localhost", role: "ADMIN" });
const managerToken = createAccessToken({ sub: "manager-1", email: "manager@localhost", role: "MANAGER" });

function jsonRequest(url: string, method: string, body?: unknown, token = adminToken): NextRequest {
  return new NextRequest(url, {
    method,
    headers: { "content-type": "application/json", authorization: `Bearer ${token}` },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
}

function prismaKnownError(code: string): Prisma.PrismaClientKnownRequestError {
  const error = Object.create(Prisma.PrismaClientKnownRequestError.prototype) as Prisma.PrismaClientKnownRequestError;
  Object.assign(error, { code });
  return error;
}

test("POST /api/bom returns 400 for invalid items", async () => {
  const request = jsonRequest("http://localhost/api/bom", "POST", {
    finishedProductId: "product-1",
    items: [],
  });

  const response = await createBom(request);
  assert.equal(response.status, 400);
});

test("POST /api/bom requires admin role", async () => {
  const unauthenticatedResponse = await createBom(
    new NextRequest("http://localhost/api/bom", { method: "POST" }),
  );
  assert.equal(unauthenticatedResponse.status, 401);

  const managerRequest = jsonRequest(
    "http://localhost/api/bom",
    "POST",
    { finishedProductId: "product-1", items: [{ componentId: "component-1", quantity: 1 }] },
    managerToken,
  );
  const forbiddenResponse = await createBom(managerRequest);
  assert.equal(forbiddenResponse.status, 403);
});

test("POST /api/bom returns 400 for duplicate components", async () => {
  const request = jsonRequest("http://localhost/api/bom", "POST", {
    finishedProductId: "product-1",
    items: [
      { componentId: "component-1", quantity: 1 },
      { componentId: "component-1", quantity: 2 },
    ],
  });

  const response = await createBom(request);
  assert.equal(response.status, 400);
});

test("POST /api/bom returns 400 for non-finite quantity", async () => {
  const request = new NextRequest("http://localhost/api/bom", {
    method: "POST",
    headers: { "content-type": "application/json", authorization: `Bearer ${adminToken}` },
    body: '{"finishedProductId":"product-1","items":[{"componentId":"component-1","quantity":1e999}]}'
  });

  const response = await createBom(request);
  assert.equal(response.status, 400);
});

test("POST /api/bom maps duplicate finished product to 409", async () => {
  const originalTransaction = prisma.$transaction;
  prisma.$transaction = async () => {
    throw prismaKnownError("P2002");
  };

  try {
    const request = jsonRequest("http://localhost/api/bom", "POST", {
      finishedProductId: "product-1",
      items: [{ componentId: "component-1", quantity: 1 }],
    });

    const response = await createBom(request);
    assert.equal(response.status, 409);
  } finally {
    prisma.$transaction = originalTransaction;
  }
});

test("PATCH /api/bom/[id] returns 400 for empty payload", async () => {
  const request = jsonRequest("http://localhost/api/bom/id-1", "PATCH", {});
  const response = await updateBom(request, { params: Promise.resolve({ id: "id-1" }) });
  assert.equal(response.status, 400);
});

test("PATCH /api/bom/[id] maps duplicate finished product to 409", async () => {
  const originalTransaction = prisma.$transaction;
  prisma.$transaction = async () => {
    throw prismaKnownError("P2002");
  };

  try {
    const request = jsonRequest("http://localhost/api/bom/id-1", "PATCH", {
      finishedProductId: "product-2",
    });
    const response = await updateBom(request, { params: Promise.resolve({ id: "id-1" }) });
    assert.equal(response.status, 409);
  } finally {
    prisma.$transaction = originalTransaction;
  }
});

test("PATCH /api/bom/[id] maps not found conflict to 404", async () => {
  const originalTransaction = prisma.$transaction;
  prisma.$transaction = async () => {
    throw prismaKnownError("P2025");
  };

  try {
    const request = jsonRequest("http://localhost/api/bom/id-1", "PATCH", {
      finishedProductId: "product-2",
    });
    const response = await updateBom(request, { params: Promise.resolve({ id: "id-1" }) });
    assert.equal(response.status, 404);
  } finally {
    prisma.$transaction = originalTransaction;
  }
});

test("POST /api/bom returns 400 when finished product type is invalid", async () => {
  const originalTransaction = prisma.$transaction;
  prisma.$transaction = async (callback) => {
    const tx = {
      product: {
        findUnique: async () => ({ id: "finished-1", type: "COMPONENT" }),
        findMany: async () => [],
      },
      bom: {
        create: async () => ({}),
      },
    } as never;

    return callback(tx);
  };

  try {
    const request = jsonRequest("http://localhost/api/bom", "POST", {
      finishedProductId: "finished-1",
      items: [{ componentId: "component-1", quantity: 1 }],
    });

    const response = await createBom(request);
    assert.equal(response.status, 400);
  } finally {
    prisma.$transaction = originalTransaction;
  }
});

test("DELETE /api/bom/[id] maps not found to 404", async () => {
  const originalDelete = prisma.bom.delete;
  prisma.bom.delete = async () => {
    throw prismaKnownError("P2025");
  };

  try {
    const response = await deleteBom(new NextRequest("http://localhost/api/bom/id-1", {
      headers: { authorization: `Bearer ${adminToken}` },
    }), {
      params: Promise.resolve({ id: "id-1" }),
    });
    assert.equal(response.status, 404);
  } finally {
    prisma.bom.delete = originalDelete;
  }
});
