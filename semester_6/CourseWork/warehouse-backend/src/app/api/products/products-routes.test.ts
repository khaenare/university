import assert from "node:assert/strict";
import test from "node:test";

import { Prisma, ProductType } from "@prisma/client";
import { NextRequest } from "next/server";

import { POST as createProduct } from "@/app/api/products/route";
import { DELETE as deleteProduct, PATCH as updateProduct } from "@/app/api/products/[id]/route";
import { createAccessToken } from "@/lib/auth";
import { prisma } from "@/lib/prisma";

const adminToken = createAccessToken({ sub: "admin-1", email: "admin@localhost", role: "ADMIN" });
const managerToken = createAccessToken({ sub: "manager-1", email: "manager@localhost", role: "MANAGER" });

const mockProduct = {
  id: "product-1",
  sku: "SKU-1",
  name: "Bolt",
  unit: "pcs",
  type: ProductType.COMPONENT,
  isActive: true,
  createdAt: new Date(),
  updatedAt: new Date(),
};

function jsonRequest(url: string, method: string, body?: unknown, token = adminToken): NextRequest {
  return new NextRequest(url, {
    method,
    headers: {
      "content-type": "application/json",
      authorization: `Bearer ${token}`,
    },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
}

function prismaKnownError(code: string): Prisma.PrismaClientKnownRequestError {
  const error = Object.create(Prisma.PrismaClientKnownRequestError.prototype) as Prisma.PrismaClientKnownRequestError;
  Object.assign(error, { code });
  return error;
}

test("POST /api/products returns 400 for invalid sku type", async () => {
  const request = jsonRequest("http://localhost/api/products", "POST", {
    sku: 10,
    name: "Name",
    unit: "pcs",
    type: ProductType.COMPONENT,
  });

  const response = await createProduct(request);
  assert.equal(response.status, 400);
});

test("POST /api/products requires admin role", async () => {
  const managerRequest = jsonRequest(
    "http://localhost/api/products",
    "POST",
    { sku: "SKU-1", name: "Name", unit: "pcs", type: ProductType.COMPONENT },
    managerToken,
  );
  const forbiddenResponse = await createProduct(managerRequest);
  assert.equal(forbiddenResponse.status, 403);

  const unauthenticatedResponse = await createProduct(
    new NextRequest("http://localhost/api/products", { method: "POST" }),
  );
  assert.equal(unauthenticatedResponse.status, 401);
});

test("POST /api/products maps duplicate sku to 409", async () => {
  const originalCreate = prisma.product.create;
  prisma.product.create = async () => {
    throw prismaKnownError("P2002");
  };

  try {
    const request = jsonRequest("http://localhost/api/products", "POST", {
      sku: "SKU-1",
      name: "Name",
      unit: "pcs",
      type: ProductType.COMPONENT,
    });

    const response = await createProduct(request);
    assert.equal(response.status, 409);
  } finally {
    prisma.product.create = originalCreate;
  }
});

test("PATCH /api/products/[id] returns 400 for invalid body type", async () => {
  const request = jsonRequest("http://localhost/api/products/1", "PATCH", {
    isActive: "yes",
  });

  const response = await updateProduct(request, { params: Promise.resolve({ id: "1" }) });
  assert.equal(response.status, 400);
});

test("PATCH /api/products/[id] returns 400 for empty payload", async () => {
  const request = jsonRequest("http://localhost/api/products/1", "PATCH", {});

  const response = await updateProduct(request, { params: Promise.resolve({ id: "1" }) });
  assert.equal(response.status, 400);
});

test("PATCH /api/products/[id] maps duplicate sku to 409", async () => {
  const originalUpdate = prisma.product.update;
  prisma.product.update = async () => {
    throw prismaKnownError("P2002");
  };

  try {
    const request = jsonRequest("http://localhost/api/products/1", "PATCH", {
      sku: "SKU-2",
    });

    const response = await updateProduct(request, { params: Promise.resolve({ id: "1" }) });
    assert.equal(response.status, 409);
  } finally {
    prisma.product.update = originalUpdate;
  }
});

test("DELETE /api/products/[id] maps FK conflict to 409", async () => {
  const originalDelete = prisma.product.delete;
  prisma.product.delete = async () => {
    throw prismaKnownError("P2003");
  };

  try {
    const response = await deleteProduct(new NextRequest("http://localhost/api/products/1", {
      headers: { authorization: `Bearer ${adminToken}` },
    }), {
      params: Promise.resolve({ id: "1" }),
    });
    assert.equal(response.status, 409);
  } finally {
    prisma.product.delete = originalDelete;
  }
});

test("DELETE /api/products/[id] returns 204 on success", async () => {
  const originalDelete = prisma.product.delete;
  prisma.product.delete = async () => mockProduct;

  try {
    const response = await deleteProduct(new NextRequest("http://localhost/api/products/1", {
      headers: { authorization: `Bearer ${adminToken}` },
    }), {
      params: Promise.resolve({ id: "1" }),
    });

    assert.equal(response.status, 204);
  } finally {
    prisma.product.delete = originalDelete;
  }
});
