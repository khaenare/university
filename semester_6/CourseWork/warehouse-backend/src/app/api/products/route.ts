import { Prisma } from "@prisma/client";
import { NextRequest, NextResponse } from "next/server";

import { OPERATOR_ROLES, requireRole } from "@/lib/authorization";
import { parseJsonObjectBody } from "@/lib/http";
import { prisma } from "@/lib/prisma";
import {
  ProductValidationError,
  requireProductName,
  requireProductSku,
  requireProductType,
  requireProductUnit,
  validateOptionalBoolean,
} from "@/lib/products";

type CreateProductBody = {
  sku?: string;
  name?: string;
  unit?: string;
  type?: string;
  isActive?: boolean;
};

export async function GET(request: NextRequest) {
  const authorizationError = requireRole(request, OPERATOR_ROLES);

  if (authorizationError) {
    return authorizationError;
  }

  const products = await prisma.product.findMany({
    orderBy: { createdAt: "desc" },
  });

  return NextResponse.json(products);
}

export async function POST(request: NextRequest) {
  const authorizationError = requireRole(request, ["ADMIN"]);

  if (authorizationError) {
    return authorizationError;
  }

  const parsedBody = await parseJsonObjectBody<CreateProductBody>(request);

  if (parsedBody instanceof NextResponse) {
    return parsedBody;
  }

  try {
    const product = await prisma.product.create({
      data: {
        sku: requireProductSku(parsedBody.sku),
        name: requireProductName(parsedBody.name),
        unit: requireProductUnit(parsedBody.unit),
        type: requireProductType(parsedBody.type),
        isActive: validateOptionalBoolean(parsedBody.isActive, "isActive") ?? true,
      },
    });

    return NextResponse.json(product, { status: 201 });
  } catch (error) {
    if (error instanceof ProductValidationError) {
      return NextResponse.json({ message: error.message }, { status: 400 });
    }

    if (error instanceof Prisma.PrismaClientKnownRequestError && error.code === "P2002") {
      return NextResponse.json({ message: "Product with this SKU already exists." }, { status: 409 });
    }

    throw error;
  }
}
